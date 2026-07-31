"""Version management and release tagging subsystem."""
from .versioning_engine import VersioningEngine
from .version_manager import VersionManager
from .tag_manager import TagManager
from .branch_manager import BranchManager
from .dependency_resolver import DependencyResolver
from .versioning_manager import VersioningManager
from .models import Version, VersionType, Branch, Tag, DependencyGraph, VersionConstraint
