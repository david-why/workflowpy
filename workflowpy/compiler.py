import ast as a
from enum import Enum, IntEnum
from typing import Any, NoReturn, cast
import uuid

from pydantic import BaseModel, ConfigDict, Field

from workflowpy import value_type as T
from workflowpy.modules import modules
from workflowpy.models.shortcuts import Action
from workflowpy.synthesizer import Synthesizer
from workflowpy.value import (
    ConstantValue,
    PythonActionBuilderValue,
    PythonValue,
    TokenAttachmentValue,
    TokenStringValue,
    Value,
    VariableValue,
)


class ScopeType(IntEnum):
    GLOBAL = 1
    FUNCTION = 2
    FOREACH = 3
    FORCOUNTER = 4


class Scope(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str | None
    type: ScopeType
    actions: list[Action] = Field(default_factory=list)
    variables: dict[str, Value] = Field(default_factory=dict)

    def add_action(self, identifier: str, parameters: dict[str, Any]):
        action = Action(
            WFWorkflowActionIdentifier=identifier,
            WFWorkflowActionParameters=parameters,
        )
        self.actions.append(action)


class Compiler(a.NodeVisitor):
    """
    This class is responsible for compiling Python code to actions.
    """

    def _push_scope(self, name: str | None, type: ScopeType):
        self.scopes.append(Scope(name=name, type=type))

    def _pop_scope(self):
        scope = self.scopes.pop()
        assert scope.type != ScopeType.GLOBAL
        if scope.type == ScopeType.FUNCTION:
            assert scope.name
            self.functions[scope.name] = scope
        else:
            self.actions.extend(scope.actions)

    def _count_scopes(self, *types: ScopeType):
        count = 0
        for scope in self.scopes:
            if scope.type in types:
                count += 1
        return count

    @property
    def variables(self):
        return self.scopes[-1].variables

    @property
    def actions(self):
        return self.scopes[-1].actions

    def compile(self, module: a.Module | str):
        self.scopes: list[Scope] = [
            Scope(name=None, type=ScopeType.GLOBAL, variables=modules[''].copy())
        ]
        self.functions: dict[str, Scope] = {}
        if isinstance(module, str):
            module = a.parse(module)
        self.visit(module)

        synthesizer = Synthesizer()
        if self.functions:
            raise NotImplementedError("Functions are not implemented yet!")
        synthesizer.actions.extend(self.scopes[0].actions)
        synthesizer.functions.update({k: v.actions for k, v in self.functions.items()})
        return synthesizer.synthesize()

    visit_Module = visit_Expr = a.NodeVisitor.generic_visit

    def visit_ImportFrom(self, node: a.ImportFrom) -> Any:
        assert node.level == 0, "Relative imports are not supported"
        parts = cast(str, node.module).split('.')
        mod = modules
        for part in parts:
            try:
                mod = mod[part]
            except KeyError:
                raise NotImplementedError(
                    f"Module {node.module!r} is not supported"
                ) from None
        for name in node.names:
            if name.name == '*':
                for key in mod:
                    self.variables[key] = mod[key]
            else:
                self.variables[name.asname or name.name] = mod[name.name]

    def visit_Assign(self, node: a.Assign) -> Any:
        # TODO multiple targets
        if len(node.targets) > 1:
            raise NotImplementedError(
                "Assign with more than one targets is not supported"
            )
        if isinstance(node.targets[0], a.Name):
            var_name = node.targets[0].id
            value = self.visit(node.value)
            self.variables[var_name] = value
        else:
            # TODO
            raise NotImplementedError(
                f"Assign with targets {node.targets} is not supported"
            )

    def visit_Call(self, node: a.Call) -> Any:
        func = self.visit(node.func)
        args = [self.visit(a) for a in node.args]
        kws = {kw.arg: self.visit(kw.value) for kw in node.keywords}
        if None in kws:
            raise NotImplementedError("**kwargs in Call is not supported")
        kws = cast(dict[str, Any], kws)
        if isinstance(func, PythonActionBuilderValue):
            result = func(self.actions, *args, **kws)
            return result
        else:
            raise NotImplementedError(f"Call with func {func} is not supported")

    def visit_For(self, node: a.For) -> Any:
        if node.orelse:
            raise NotImplementedError("else: is not supported in For statements")
        count_of_for = self._count_scopes(ScopeType.FORCOUNTER, ScopeType.FOREACH)
        suffix = '' if count_of_for == 0 else f' {count_of_for+1}'
        grouping_uuid = str(uuid.uuid4()).upper()
        if (
            isinstance(node.iter, a.Call)
            and isinstance(node.iter.func, a.Name)
            and node.iter.func.id == 'range'
        ):
            assert isinstance(
                node.target, a.Name
            ), "Only simple loop variables are supported"
            assert (
                not node.iter.keywords
            ), "for...range constructs cannot have keyword arguments"
            range_args = node.iter.args
            # TODO support range(len(X))
            if len(range_args) == 1:
                range_start = ConstantValue(0)
                range_end = self.visit(range_args[0])
            elif len(range_args) == 2:
                range_start = self.visit(range_args[0])
                range_end = self.visit(range_args[1])
            elif len(range_args) == 3:
                raise NotImplementedError("for...range with step is not supported")
            else:
                raise ValueError("for...range has incorrect arguments")
            count_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.calculateexpression',
                WFWorkflowActionParameters={
                    'Input': TokenStringValue(
                        range_end, ' - ', range_start, ' + 1'
                    ).synthesize(self.actions)
                },
            ).with_output('Calculation Result', T.number)
            self.actions.append(count_action)
            count_value = count_action.output
            assert count_value
            start_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.count',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 0,
                    'WFRepeatCount': TokenAttachmentValue(count_value).synthesize(
                        self.actions
                    ),
                },
            )
            end_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.count',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 2,
                },
            )
            self._push_scope(None, ScopeType.FORCOUNTER)
            self.variables[node.target.id] = VariableValue(f'Repeat Index{suffix}')
        elif (
            isinstance(node.iter, a.Call)
            and isinstance(node.iter.func, a.Name)
            and node.iter.func.id == 'enumerate'
        ):
            assert (
                not node.iter.keywords and len(node.iter.args) == 1
            ), "for...enumerate has incorrect arguments"
            assert (
                isinstance(node.target, a.Tuple)
                and len(node.target.elts) == 2
                and isinstance(node.target.elts[0], a.Name)
                and isinstance(node.target.elts[1], a.Name)
            ), "Only two loop variables in a tuple is supported"
            iterable = self.visit(node.iter.args[0])
            start_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 0,
                    'WFInput': TokenAttachmentValue(iterable).synthesize(self.actions),
                },
            )
            end_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 2,
                },
            )
            self._push_scope(None, ScopeType.FOREACH)
            self.variables[node.target.elts[0].id] = VariableValue(
                f'Repeat Index{suffix}'
            )
            self.variables[node.target.elts[1].id] = VariableValue(
                f'Repeat Item{suffix}'
            )
        else:
            assert isinstance(
                node.target, a.Name
            ), "Only simple loop variables are supported"
            iterable = self.visit(node.iter)
            start_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 0,
                    'WFInput': TokenAttachmentValue(iterable).synthesize(self.actions),
                },
            )
            end_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 2,
                },
            )
            self._push_scope(None, ScopeType.FOREACH)
            self.variables[node.target.id] = VariableValue(f'Repeat Item{suffix}')

        self.actions.append(start_action)
        for stmt in node.body:
            self.visit(stmt)
        self.actions.append(end_action)
        self._pop_scope()

    # expressions; all should return a Value

    def visit_Name(self, node: a.Name) -> Any:
        for scope in self.scopes[::-1]:
            if node.id in scope.variables:
                return scope.variables[node.id]
        raise NameError(f"Name {node.id!r} is not found")

    def visit_Constant(self, node: a.Constant) -> Any:
        if isinstance(node.value, (str, int, float)):
            return ConstantValue(node.value)
        raise TypeError(
            f'Constants of type {node.value.__class__.__name__} are not supported'
        )

    def visit_JoinedStr(self, node: a.JoinedStr) -> Any:
        parts = [self.visit(x) for x in node.values]
        return TokenStringValue(*parts)

    def visit_FormattedValue(self, node: a.FormattedValue) -> Any:
        if node.format_spec or node.conversion != -1:
            raise NotImplementedError("Conversions in F-strings are not supported")
        return self.visit(node.value)

    def visit_List(self, node: a.List) -> Any:
        values = [
            TokenStringValue(self.visit(x)).synthesize(self.actions) for x in node.elts
        ]
        action = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.list',
            WFWorkflowActionParameters={'WFItems': values},
        ).with_output('List', T.any)
        self.actions.append(action)
        return action.output

    def generic_visit(self, node: a.AST) -> NoReturn:
        name = node.__class__.__name__
        raise NotImplementedError(f"{name} nodes are not implemented yet!")
