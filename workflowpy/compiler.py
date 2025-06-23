import ast as a
from typing import Any, NoReturn

from pydantic import BaseModel, Field

from workflowpy.models.shortcuts import Action
from workflowpy.synthesizer import Synthesizer
from workflowpy.value import Value


class Scope(BaseModel):
    name: str | None
    actions: list[Action] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)

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

    def push_scope(self, func_name: str | None):
        self.scopes.append(Scope(name=func_name))

    def pop_scope(self):
        scope = self.scopes.pop()
        assert scope.name
        self.functions[scope.name] = scope

    def compile(self, module: a.Module | str):
        self.scopes: list[Scope] = [Scope(name=None)]
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
        if node.module == 'workflowpy':
            return
        raise NotImplementedError(f"Module {node.module} is not implemented yet!")

    def generic_visit(self, node: a.AST) -> NoReturn:
        name = node.__class__.__name__
        raise NotImplementedError(f"{name} nodes are not implemented yet!")
