"""Actor Selector — picks the best catalog voice for a character description."""
from __future__ import annotations

from modules.ai_video_studio.ai_voice_studio import get_voice_engine

# Role hints → voice ids (best-effort mapping onto the catalog).
_ROLE_VOICES: dict[str, str] = {
    "narrator": "default",
    "narrator_female": "aria",
    "narrator_male": "guy",
    "male": "guy",
    "female": "aria",
    "child": "child_boy",
    "elderly": "elderly_man",
    "villain": "male_gruff",
    "hero": "male_deep",
    "heroine": "female_warm",
    "comic": "female_energetic",
    "corporate": "corporate_man",
    "documentary": "doc_uk_male",
    "advertising": "ad_energetic",
}


def select_voice(role: str | None = None, gender: str | None = None,
                 language: str = "en") -> str:
    """Resolve a voice id from role/gender hints."""
    key = f"{role or ''}".lower().strip()
    if key in _ROLE_VOICES:
        voice = _ROLE_VOICES[key]
    elif gender == "female":
        voice = "female_warm"
    elif gender == "male":
        voice = "male_friendly"
    else:
        voice = "default"

    # Prefer a voice that speaks the target language.
    for v in get_voice_engine().list_voices():
        if v["id"] == voice and v["language"].lower().startswith(language.lower().split("-")[0]):
            return voice
    for v in get_voice_engine().list_voices():
        if v["language"].lower().startswith(language.lower().split("-")[0]):
            return v["id"]
    return voice
