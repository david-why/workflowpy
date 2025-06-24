import ast as a
from enum import Enum, IntEnum
from typing import Any, NoReturn, cast

from pydantic import BaseModel, ConfigDict, Field

from workflowpy.modules import modules
from workflowpy.models.shortcuts import Action
from workflowpy.synthesizer import Synthesizer
from workflowpy.value import (
    ConstantValue,
    PythonActionBuilderValue,
    PythonValue,
    TokenStringValue,
    Value,
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
        if (
            isinstance(node.iter, a.Call)
            and isinstance(node.iter.func, a.Name)
            and node.iter.func.id == 'range'
        ):
            assert (
                not node.iter.keywords
            ), "for...range constructs cannot have keyword arguments"
            range_args = node.iter.args
            # TODO support range(len(X))
            assert all(
                isinstance(x, a.Constant) and isinstance(x.value, int)
                for x in range_args
            ), "All arguments to for...range must be literal integers"
            range_args = cast(list[a.Constant], range_args)
            if len(range_args) == 1:
                range_start = 0
                range_end = cast(int, range_args[0].value)
            elif len(range_args) == 2:
                range_start = cast(int, range_args[0].value)
                range_end = cast(int, range_args[1].value)
            elif len(range_args) == 3:
                raise NotImplementedError("for...range with step is not supported")
            else:
                raise ValueError("for...range has incorrect arguments")
            count = range_end - range_start + 1
            assert count >= 0, "for...range has no iterations"


    # expressions

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
        )

    def generic_visit(self, node: a.AST) -> NoReturn:
        name = node.__class__.__name__
        raise NotImplementedError(f"{name} nodes are not implemented yet!")
