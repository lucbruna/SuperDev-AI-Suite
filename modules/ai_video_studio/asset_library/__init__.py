"""Asset Library — reusable creative asset registry (blueprint Volume 3).

Manages assets with indexing, search, tagging, versioning plus specialised
libraries for textures, materials, objects, characters, vehicles, buildings,
vegetation, skies, sounds, music and effects.
"""
from modules.ai_video_studio.asset_library.asset_manager import AssetManager
from modules.ai_video_studio.asset_library.asset_index import AssetIndex
from modules.ai_video_studio.asset_library.asset_search import AssetSearch
from modules.ai_video_studio.asset_library.asset_tags import AssetTags
from modules.ai_video_studio.asset_library.asset_versions import AssetVersions
from modules.ai_video_studio.asset_library.texture_library import TextureLibrary
from modules.ai_video_studio.asset_library.material_library import MaterialLibrary
from modules.ai_video_studio.asset_library.object_library import ObjectLibrary
from modules.ai_video_studio.asset_library.character_library import CharacterLibrary
from modules.ai_video_studio.asset_library.vehicle_library import VehicleLibrary
from modules.ai_video_studio.asset_library.building_library import BuildingLibrary
from modules.ai_video_studio.asset_library.vegetation_library import VegetationLibrary
from modules.ai_video_studio.asset_library.sky_library import SkyLibrary
from modules.ai_video_studio.asset_library.sound_library import SoundLibrary
from modules.ai_video_studio.asset_library.music_library import MusicLibrary
from modules.ai_video_studio.asset_library.effects_library import EffectsLibrary

__all__ = [
    "AssetManager",
    "AssetIndex",
    "AssetSearch",
    "AssetTags",
    "AssetVersions",
    "TextureLibrary",
    "MaterialLibrary",
    "ObjectLibrary",
    "CharacterLibrary",
    "VehicleLibrary",
    "BuildingLibrary",
    "VegetationLibrary",
    "SkyLibrary",
    "SoundLibrary",
    "MusicLibrary",
    "EffectsLibrary",
]
