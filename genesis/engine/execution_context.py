from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable runtime container shared across engine, routines and flows.
    
    Holds infrastructure references and static runtime data.
    Contains NO business logic.
    """

    browser_manager: Any
    runtime_config: Dict
    blueprint: Dict
