import ast as a
from typing import Any, NoReturn, cast

from pydantic import BaseModel, ConfigDict, Field

from workflowpy.modules import modules
from workflowpy.models.shortcuts import Action
from workflowpy.synthesizer import Synthesizer
from workflowpy.value import PythonActionBuilderValue, PythonValue, Value


class Scope(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str | None
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

    def _push_scope(self, func_name: str | None):
        self.scopes.append(Scope(name=func_name))

    def _pop_scope(self):
        scope = self.scopes.pop()
        assert scope.name
        self.functions[scope.name] = scope

    @property
    def variables(self):
        return self.scopes[-1].variables

    def compile(self, module: a.Module | str):
        self.scopes: list[Scope] = [Scope(name=None, variables=modules[''].copy())]
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

    visit_Module = a.NodeVisitor.generic_visit

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
            result = func(self.scopes[-1].actions, *args, **kws)
            return result
        else:
            raise NotImplementedError(f"Call with func {func} is not supported")

    # expressions
    
    def visit_Name(self, node: a.Name) -> Any:
        for scope in self.scopes[::-1]:
            if node.id in scope.variables:
                return scope.variables[node.id]
        raise NameError(f"Name {node.id!r} is not found")

    def generic_visit(self, node: a.AST) -> NoReturn:
        name = node.__class__.__name__
        raise NotImplementedError(f"{name} nodes are not implemented yet!")
