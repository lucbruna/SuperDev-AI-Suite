"""Version management and release tagging subsystem."""

from .branch_manager import BranchManager
from .dependency_resolver import DependencyResolver
from .models import Branch, DependencyGraph, Tag, Version, VersionConstraint, VersionType
from .tag_manager import TagManager
from .version_manager import VersionManager
from .versioning_engine import VersioningEngine
from .versioning_manager import VersioningManager
