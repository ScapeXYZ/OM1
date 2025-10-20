import time
import typing as T
from abc import ABC, abstractmethod
from dataclasses import dataclass

IT = T.TypeVar("IT")
OT = T.TypeVar("OT")


@dataclass
class MoveCommand:
    dx: float
    yaw: float
    start_x: float = 0.0
    start_y: float = 0.0
    turn_complete: bool = False
    speed: float = 0.5


@dataclass
class ActionConfig:
    """
    Configuration class for Action implementations.

    Parameters
    ----------
    **kwargs : dict
        Additional configuration parameters
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class Interface(T.Generic[IT, OT]):
    """An interface for a generic action."""
    input: IT
    output: OT


class ActionConnector(ABC, T.Generic[IT, OT]):
    def __init__(self, config: ActionConfig):
        self.config = config

    @abstractmethod
    async def connect(self, input_protocol: OT) -> None:
        pass

    def tick(self) -> None:
        time.sleep(60)


@dataclass
class AgentAction:
    """Base class for agent actions."""
    name: str
    llm_label: str
    interface: T.Type[Interface]
    connector: ActionConnector
    exclude_from_prompt: bool


# --- Custom Extension for External Action Interfaces ---
class BaseActionInterface:
    """
    Simple base interface for external integrations like Home Assistant.
    Provides a structure for perform_action() to be implemented by subclasses.
    """
    def __init__(self, config=None):
        self.config = config

    def perform_action(self, *args, **kwargs):
        raise NotImplementedError("perform_action() must be implemented by subclass.")
