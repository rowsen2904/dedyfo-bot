"""Core package for dependency injection and application setup."""

from .container import Container
from .dependencies import get_container

__all__ = ["Container", "get_container"]
