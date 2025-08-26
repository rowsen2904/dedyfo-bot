"""Professional bot package with dependency injection."""

from .core.container import Container
from .core.dependencies import get_container

__version__ = "2.0.0"
__all__ = ["Container", "get_container"]
