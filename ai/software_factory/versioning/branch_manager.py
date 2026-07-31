"""Manager for version control branches."""

from .models import Branch


class BranchManager:
    def __init__(self):
        self._branches: list[Branch] = []

    def create_branch(self, name: str, source: str = "main") -> Branch:
        branch = Branch(name=name, source_branch=source)
        self._branches.append(branch)
        return branch

    def get_branch(self, name: str) -> Branch | None:
        for b in self._branches:
            if b.name == name:
                return b
        return None

    def protect_branch(self, name: str) -> bool:
        branch = self.get_branch(name)
        if branch:
            branch.is_protected = True
            return True
        return False

    def merge_branch(self, name: str) -> bool:
        branch = self.get_branch(name)
        if branch:
            branch.is_merged = True
            return True
        return False

    def list_branches(self) -> list[Branch]:
        return list(self._branches)

    def count(self) -> int:
        return len(self._branches)
