"""D.A.N. Plugins - Plugin system."""

from dan.plugins.base import Plugin, PluginMetadata
from dan.plugins.decorators import plugin
from dan.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "plugin",
]

