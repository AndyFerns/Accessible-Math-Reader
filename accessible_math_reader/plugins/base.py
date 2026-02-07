"""!
@file plugins/base.py
@brief Base classes and interfaces for the plugin system.

@details
Defines abstract base classes that plugins must implement to extend
the Accessible Math Reader functionality. Supports:
- Custom speech rules for new mathematical notations
- Additional Braille notations
- New input format parsers
- Localization extensions

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional
import importlib.util
import logging

from accessible_math_reader.core.semantic import SemanticNode

if TYPE_CHECKING:
    from accessible_math_reader.config import Config

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """!
    @brief Types of plugins supported by the system.
    """
    SPEECH_RULES = "speech_rules"     ##< Custom speech verbalization rules
    BRAILLE_NOTATION = "braille"       ##< Additional Braille notation systems
    INPUT_FORMAT = "input_format"      ##< New input format parsers
    LOCALIZATION = "localization"      ##< Language/locale support


@dataclass
class PluginInfo:
    """!
    @brief Metadata about a plugin.
    
    @param name Unique identifier for the plugin
    @param version Plugin version string
    @param description Human-readable description
    @param author Plugin author
    @param plugin_type Type of plugin
    """
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType


class BasePlugin(ABC):
    """!
    @brief Abstract base class for all plugins.
    
    @details
    All plugins must inherit from this class and implement
    the required methods. Plugins are discovered and loaded
    by the PluginManager.
    
    @section plugin_example Example Plugin
    @code{.py}
    from accessible_math_reader.plugins.base import (
        BasePlugin, PluginInfo, PluginType
    )
    
    class MyCustomRulesPlugin(BasePlugin):
        @property
        def info(self) -> PluginInfo:
            return PluginInfo(
                name="my-custom-rules",
                version="1.0.0",
                description="Custom speech rules for chemistry",
                author="Your Name",
                plugin_type=PluginType.SPEECH_RULES
            )
        
        def initialize(self, config):
            # Setup plugin
            pass
        
        def cleanup(self):
            # Cleanup resources
            pass
    @endcode
    """
    
    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """!
        @brief Get plugin metadata.
        
        @return PluginInfo instance with plugin details
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Config) -> None:
        """!
        @brief Initialize the plugin with configuration.
        
        @details
        Called when the plugin is loaded. Use this to set up
        any resources the plugin needs.
        
        @param config Application configuration
        """
        pass
    
    def cleanup(self) -> None:
        """!
        @brief Clean up plugin resources.
        
        @details
        Called when the plugin is unloaded. Override to release
        any resources acquired during initialization.
        """
        pass


class SpeechRulesPlugin(BasePlugin):
    """!
    @brief Plugin for custom speech verbalization rules.
    
    @details
    Extend this class to add speech rules for new mathematical
    notations or to customize existing rules.
    """
    
    @abstractmethod
    def get_speech_rules(self) -> dict[str, Callable[[SemanticNode], str]]:
        """!
        @brief Get custom speech rendering functions.
        
        @details
        Returns a dictionary mapping node type names to functions
        that render those nodes to speech text.
        
        @return Dictionary of node_type_name -> render_function
        """
        pass


class BrailleNotationPlugin(BasePlugin):
    """!
    @brief Plugin for additional Braille notation systems.
    
    @details
    Extend this class to add support for Braille notations
    beyond Nemeth and UEB, such as French or German math Braille.
    """
    
    @property
    @abstractmethod
    def notation_name(self) -> str:
        """!
        @brief Get the name of this Braille notation.
        
        @return Notation name (e.g., "french", "german")
        """
        pass
    
    @abstractmethod
    def render(self, node: SemanticNode) -> str:
        """!
        @brief Render a semantic node to this Braille notation.
        
        @param node Semantic node to render
        @return Braille string in this notation
        """
        pass


class InputFormatPlugin(BasePlugin):
    """!
    @brief Plugin for additional input format parsers.
    
    @details
    Extend this class to add support for input formats
    beyond LaTeX and MathML.
    """
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """!
        @brief Get the name of this input format.
        
        @return Format name (e.g., "asciimath", "mathjs")
        """
        pass
    
    @abstractmethod
    def can_parse(self, input_str: str) -> bool:
        """!
        @brief Check if this parser can handle the input.
        
        @param input_str Input string to check
        @return True if this parser can handle it
        """
        pass
    
    @abstractmethod
    def parse(self, input_str: str) -> SemanticNode:
        """!
        @brief Parse input to semantic tree.
        
        @param input_str Input string in this format
        @return Root SemanticNode of parsed expression
        """
        pass


class PluginManager:
    """!
    @brief Manages plugin discovery, loading, and lifecycle.
    
    @details
    Scans plugin directories for valid plugins, loads them,
    and provides access to their functionality.
    
    @section manager_example Example Usage
    @code{.py}
    from accessible_math_reader.plugins.base import PluginManager
    from accessible_math_reader.config import Config
    
    config = Config()
    config.plugin_dirs = ["./plugins"]
    
    manager = PluginManager(config)
    manager.discover_plugins()
    manager.load_all()
    
    # Get speech rules from all plugins
    rules = manager.get_speech_rules()
    @endcode
    """
    
    def __init__(self, config: Config) -> None:
        """!
        @brief Initialize plugin manager.
        
        @param config Application configuration
        """
        self.config = config
        self._plugins: dict[str, BasePlugin] = {}
        self._discovered: list[Path] = []
    
    def discover_plugins(self) -> list[Path]:
        """!
        @brief Discover plugins in configured directories.
        
        @details
        Scans plugin directories for Python files that might
        contain plugin implementations.
        
        @return List of discovered plugin file paths
        """
        self._discovered = []
        
        for plugin_dir in self.config.plugin_dirs:
            path = Path(plugin_dir)
            if not path.exists():
                logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue
            
            # Find Python files
            for py_file in path.glob("*.py"):
                if not py_file.name.startswith("_"):
                    self._discovered.append(py_file)
            
            # Find packages
            for pkg_dir in path.iterdir():
                if pkg_dir.is_dir() and (pkg_dir / "__init__.py").exists():
                    self._discovered.append(pkg_dir / "__init__.py")
        
        logger.info(f"Discovered {len(self._discovered)} potential plugins")
        return self._discovered
    
    def load_plugin(self, path: Path) -> Optional[BasePlugin]:
        """!
        @brief Load a single plugin from a file path.
        
        @param path Path to plugin Python file
        @return Loaded plugin instance, or None if loading failed
        """
        try:
            spec = importlib.util.spec_from_file_location(
                path.stem, 
                str(path)
            )
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in module
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, BasePlugin) and 
                    obj is not BasePlugin and
                    not name.startswith("_")):
                    
                    # Instantiate and initialize
                    plugin = obj()
                    plugin.initialize(self.config)
                    self._plugins[plugin.info.name] = plugin
                    logger.info(f"Loaded plugin: {plugin.info.name}")
                    return plugin
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {path}: {e}")
            return None
    
    def load_all(self) -> int:
        """!
        @brief Load all discovered plugins.
        
        @return Number of successfully loaded plugins
        """
        count = 0
        for path in self._discovered:
            if self.load_plugin(path):
                count += 1
        return count
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """!
        @brief Get a loaded plugin by name.
        
        @param name Plugin name
        @return Plugin instance or None
        """
        return self._plugins.get(name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> list[BasePlugin]:
        """!
        @brief Get all loaded plugins of a specific type.
        
        @param plugin_type Type of plugins to retrieve
        @return List of plugins of that type
        """
        return [
            p for p in self._plugins.values()
            if p.info.plugin_type == plugin_type
        ]
    
    def get_speech_rules(self) -> dict[str, Callable[[SemanticNode], str]]:
        """!
        @brief Get all custom speech rules from loaded plugins.
        
        @return Combined dictionary of speech rules
        """
        rules = {}
        for plugin in self.get_plugins_by_type(PluginType.SPEECH_RULES):
            if isinstance(plugin, SpeechRulesPlugin):
                rules.update(plugin.get_speech_rules())
        return rules
    
    def get_braille_notations(self) -> dict[str, BrailleNotationPlugin]:
        """!
        @brief Get all custom Braille notations from plugins.
        
        @return Dictionary of notation_name -> plugin
        """
        notations = {}
        for plugin in self.get_plugins_by_type(PluginType.BRAILLE_NOTATION):
            if isinstance(plugin, BrailleNotationPlugin):
                notations[plugin.notation_name] = plugin
        return notations
    
    def unload_all(self) -> None:
        """!
        @brief Unload all plugins and clean up resources.
        """
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin.info.name}: {e}")
        
        self._plugins.clear()
        logger.info("All plugins unloaded")
