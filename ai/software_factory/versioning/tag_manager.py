"""Manager for version tags."""

from .models import Tag


class TagManager:
    def __init__(self):
        self._tags: list[Tag] = []

    def create_tag(self, name: str, version: str, message: str = "") -> Tag:
        tag = Tag(name=name, version=version, message=message)
        self._tags.append(tag)
        return tag

    def get_tag(self, name: str) -> Tag | None:
        for t in self._tags:
            if t.name == name:
                return t
        return None

    def list_tags(self) -> list[Tag]:
        return list(self._tags)

    def delete_tag(self, name: str) -> bool:
        for i, t in enumerate(self._tags):
            if t.name == name:
                self._tags.pop(i)
                return True
        return False

    def count(self) -> int:
        return len(self._tags)
