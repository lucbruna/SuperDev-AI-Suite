"""AI Music Generator — real music synthesis (Volume 4).

20 genres, 10 instruments, real chord progressions and real rendered audio
(WAV/MP3) via numpy synthesis.
"""
from modules.ai_video_studio.ai_music_generator.music_engine import MusicEngine, get_music_engine
from modules.ai_video_studio.ai_music_generator.music_models import Note, Track, Song
from modules.ai_video_studio.ai_music_generator.music_library import note_frequency, scale_notes, chord_tones
from modules.ai_video_studio.ai_music_generator.genres import list_genres

__all__ = [
    "MusicEngine",
    "get_music_engine",
    "Note",
    "Track",
    "Song",
    "note_frequency",
    "scale_notes",
    "chord_tones",
    "list_genres",
]
