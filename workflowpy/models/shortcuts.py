from typing import Any, Literal, Self
import uuid

from pydantic import BaseModel, Field, field_validator, model_validator


type ContentItemClass = str
type ShortcutType = Literal[
    "QuickActions", "MenuBar", "ActionExtension", "ReceivesOnScreenContent"
]


class Action(BaseModel):
    WFWorkflowActionIdentifier: str
    WFWorkflowActionParameters: dict[str, Any] = Field(default_factory=dict)

    @property
    def uuid(self) -> str | None:
        return self.WFWorkflowActionParameters.get('UUID')

    def with_output(self) -> Self:
        self.WFWorkflowActionParameters.setdefault('UUID', str(uuid.uuid4()).upper())
        return self


class ShortcutIcon(BaseModel):
    WFWorkflowIconGlyphNumber: int = 61440
    WFWorkflowIconStartColor: int = -615917313


class ImportQuestion(BaseModel):
    ActionIndex: int
    Category: Literal["Parameter"]
    DefaultValue: Any = None
    ParameterKey: str
    Text: str | None = None


class Shortcut(BaseModel):
    WFQuickActionSurfaces: list = []  # Always an empty list
    WFWorkflowActions: list[Action] = []
    WFWorkflowClientVersion: str = "3607.0.2"  # Constant
    WFWorkflowHasOutputFallback: bool = False
    WFWorkflowHasShortcutInputVariables: bool = False
    WFWorkflowIcon: ShortcutIcon = ShortcutIcon()
    WFWorkflowImportQuestions: list[ImportQuestion] = []
    WFWorkflowInputContentItemClasses: list[ContentItemClass] = []
    WFWorkflowIsDisabledOnLockScreen: bool = False
    WFWorkflowMinimumClientVersion: int = 900  # Constant
    WFWorkflowMinimumClientVersionString: str = "900"  # Constant
    WFWorkflowOutputContentItemClasses: list[ContentItemClass] = []
    WFWorkflowTypes: list[ShortcutType] = []
