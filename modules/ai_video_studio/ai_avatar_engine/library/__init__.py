"""Avatar Library — domain-specific virtual actor catalogs.

Each module (business, education, medical, legal, agriculture, engineering,
finance, tourism, ecommerce, influencer, presenter, child, elderly,
fantasy, sci_fi) defines a list of :class:`AvatarProfile` presets. The
``AvatarLibrary`` aggregates them all.
"""
from modules.ai_video_studio.ai_avatar_engine.library.avatar_library import (
    AvatarLibrary,
    get_avatar_library,
)

__all__ = ["AvatarLibrary", "get_avatar_library"]
