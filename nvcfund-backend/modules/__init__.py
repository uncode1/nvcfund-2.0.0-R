"""
NVC Banking Platform - Enterprise Modular Architecture
Central module registry and management system
"""

from .core.registry import module_registry

__version__ = "1.0.0"
__all__ = ["module_registry"]