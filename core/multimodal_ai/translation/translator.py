from __future__ import annotations

from typing import Any, Optional


MOCK_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "hello": "hello",
        "goodbye": "goodbye",
        "thank you": "thank you",
        "how are you?": "how are you?",
        "what is your name?": "what is your name?",
    },
    "pt": {
        "hello": "olá",
        "goodbye": "tchau",
        "thank you": "obrigado",
        "how are you?": "como você está?",
        "what is your name?": "qual é o seu nome?",
    },
    "es": {
        "hello": "hola",
        "goodbye": "adiós",
        "thank you": "gracias",
        "how are you?": "¿cómo estás?",
        "what is your name?": "¿cómo te llamas?",
    },
    "fr": {
        "hello": "bonjour",
        "goodbye": "au revoir",
        "thank you": "merci",
        "how are you?": "comment allez-vous?",
        "what is your name?": "comment vous appelez-vous?",
    },
    "de": {
        "hello": "hallo",
        "goodbye": "tschüss",
        "thank you": "danke",
        "how are you?": "wie geht es Ihnen?",
        "what is your name?": "wie heißen Sie?",
    },
    "it": {
        "hello": "ciao",
        "goodbye": "arrivederci",
        "thank you": "grazie",
        "how are you?": "come stai?",
        "what is your name?": "come ti chiami?",
    },
    "ja": {
        "hello": "こんにちは",
        "goodbye": "さようなら",
        "thank you": "ありがとう",
        "how are you?": "お元気ですか？",
        "what is your name?": "お名前は何ですか？",
    },
}


class Translator:
    def __init__(self) -> None:
        self._translations = MOCK_TRANSLATIONS
        self._quality: dict[str, float] = {}

    def translate(self, text: str, source: str, target: str) -> str:
        if source == target:
            return text
        text_lower = text.lower().strip()
        if target in self._translations and text_lower in self._translations[target]:
            result = self._translations[target][text_lower]
            if text[0].isupper():
                result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()
            return result
        if source == "en" and target in self._translations:
            return f"[{target}]{text}[/{target}]"
        return text

    def translate_batch(self, texts: list[str], source: str, target: str) -> list[str]:
        return [self.translate(t, source, target) for t in texts]

    def translate_document(self, document: str, source: str = "auto", target: str = "en") -> str:
        lines = document.split("\n")
        translated_lines = []
        for line in lines:
            if line.strip():
                translated_lines.append(self.translate(line, source, target))
            else:
                translated_lines.append(line)
        return "\n".join(translated_lines)

    def get_translation_quality(self, pair: str = "en-pt") -> float:
        return self._quality.get(pair, 0.85)
