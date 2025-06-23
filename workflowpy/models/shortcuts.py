from typing import Any, Literal

from pydantic import BaseModel, Field


type ContentItemClass = str
type ShortcutType = Literal[
    "QuickActions", "MenuBar", "ActionExtension", "ReceivesOnScreenContent"
]


class Action(BaseModel):
    WFWorkflowActionIdentifier: str
    WFWorkflowActionParameters: dict[str, Any] = Field(default_factory=dict)


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
    WFQuickActionSurfaces: list = []
    WFWorkflowActions: list[Action] = []
    WFWorkflowClientVersion: Literal["3607.0.2"] = "3607.0.2"
    WFWorkflowHasOutputFallback: bool = False
    WFWorkflowHasShortcutInputVariables: bool = False
    WFWorkflowIcon: ShortcutIcon = ShortcutIcon()
    WFWorkflowImportQuestions: list[ImportQuestion] = []
    WFWorkflowInputContentItemClasses: list[ContentItemClass] = []
    WFWorkflowIsDisabledOnLockScreen: bool = False
    WFWorkflowMinimumClientVersion: int = 900
    WFWorkflowMinimumClientVersionString: str = "900"
    WFWorkflowOutputContentItemClasses: list[ContentItemClass] = []
    WFWorkflowTypes: list[ShortcutType] = []
