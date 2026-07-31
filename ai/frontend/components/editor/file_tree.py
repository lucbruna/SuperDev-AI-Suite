"""
File Tree Component
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class NodeType(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"


@dataclass
class FileNode:
    name: str
    path: str
    type: NodeType
    children: list["FileNode"] = field(default_factory=list)
    parent: Optional["FileNode"] = None
    expanded: bool = False
    selected: bool = False
    modified: bool = False
    icon: str | None = None

    @property
    def extension(self):
        return os.path.splitext(self.name)[1] if self.type == NodeType.FILE else ""

    @property
    def is_root(self):
        return self.parent is None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, name):
        for i, child in enumerate(self.children):
            if child.name == name:
                return self.children.pop(i)
        return None

    def find_child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def find(self, path):
        parts = path.split(os.sep)
        current = self
        for part in parts:
            if part == current.name:
                continue
            child = current.find_child(part)
            if not child:
                return None
            current = child
        return current

    def toggle_expand(self):
        if self.type == NodeType.DIRECTORY:
            self.expanded = not self.expanded

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False


class FileTree:
    def __init__(self):
        self.root = FileNode(name="root", path="/", type=NodeType.DIRECTORY)
        self.selected_node = None
        self.listeners = []
        self.search_term = ""

    def add_file(self, path, parent_path="/"):
        name = os.path.basename(path)
        node = FileNode(name=name, path=path, type=NodeType.FILE)
        parent = self.root.find(parent_path)
        if parent:
            parent.add_child(node)
            self._emit("file_added", {"node": node})
        return node

    def add_directory(self, path, parent_path="/"):
        name = os.path.basename(path)
        node = FileNode(name=name, path=path, type=NodeType.DIRECTORY)
        parent = self.root.find(parent_path)
        if parent:
            parent.add_child(node)
            self._emit("directory_added", {"node": node})
        return node

    def remove(self, path):
        parts = path.split(os.sep)
        parent = self.root
        for part in parts[:-1]:
            child = parent.find_child(part)
            if not child:
                return False
            parent = child
        removed = parent.remove_child(parts[-1])
        if removed:
            self._emit("node_removed", {"path": path})
            return True
        return False

    def select(self, path):
        if self.selected_node:
            self.selected_node.deselect()
        node = self.root.find(path)
        if node:
            node.select()
            self.selected_node = node
            self._emit("node_selected", {"node": node})
        return node

    def expand_all(self):
        self._expand_recursive(self.root)

    def _expand_recursive(self, node):
        if node.type == NodeType.DIRECTORY:
            node.expanded = True
            for child in node.children:
                self._expand_recursive(child)

    def collapse_all(self):
        self._collapse_recursive(self.root)

    def _collapse_recursive(self, node):
        node.expanded = False
        for child in node.children:
            self._collapse_recursive(child)

    def search(self, term):
        results = []
        self._search_recursive(self.root, term.lower(), results)
        return results

    def _search_recursive(self, node, term, results):
        if term in node.name.lower():
            results.append(node)
        for child in node.children:
            self._search_recursive(child, term, results)

    def get_all_files(self):
        files = []
        self._get_files_recursive(self.root, files)
        return files

    def _get_files_recursive(self, node, files):
        if node.type == NodeType.FILE:
            files.append(node)
        for child in node.children:
            self._get_files_recursive(child, files)

    def on(self, event, callback):
        self.listeners.append({"event": event, "callback": callback})

    def _emit(self, event, data):
        for listener in self.listeners:
            if listener["event"] == event:
                listener["callback"](data)
