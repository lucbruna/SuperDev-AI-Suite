"""
Diff Viewer Component
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class DiffLineType(Enum):
    ADD = "add"
    REMOVE = "remove"
    EQUAL = "equal"
    HEADER = "header"
    CHUNK = "chunk"


class DiffViewMode(Enum):
    UNIFIED = "unified"
    SPLIT = "split"
    INLINE = "inline"


@dataclass
class DiffLine:
    content: str
    line_type: DiffLineType
    old_line_num: Optional[int] = None
    new_line_num: Optional[int] = None
    
    @property
    def is_change(self):
        return self.line_type in (DiffLineType.ADD, DiffLineType.REMOVE)


@dataclass
class DiffHunk:
    header: str
    lines: List[DiffLine] = field(default_factory=list)
    old_start: int = 0
    old_count: int = 0
    new_start: int = 0
    new_count: int = 0
    
    @property
    def changes(self):
        return sum(1 for l in self.lines if l.is_change)


@dataclass
class DiffFile:
    old_path: str
    new_path: str
    hunks: List[DiffHunk] = field(default_factory=list)
    status: str = "modified"
    
    @property
    def additions(self):
        return sum(sum(1 for l in h.lines if l.line_type == DiffLineType.ADD) for h in self.hunks)
    
    @property
    def deletions(self):
        return sum(sum(1 for l in h.lines if l.line_type == DiffLineType.REMOVE) for h in self.hunks)
    
    @property
    def has_changes(self):
        return self.additions > 0 or self.deletions > 0


class DiffViewer:
    def __init__(self):
        self.files = []
        self.view_mode = DiffViewMode.UNIFIED
        self.selected_file = None
        self.highlight_changes = True
        self.show_line_numbers = True
        
    def set_diff(self, old_content, new_content, old_path="", new_path=""):
        self.files.clear()
        old_lines = old_content.split("\n")
        new_lines = new_content.split("\n")
        hunks = self._compute_diff(old_lines, new_lines)
        file = DiffFile(old_path=old_path or "Original", new_path=new_path or "Modified", hunks=hunks)
        self.files.append(file)
        self.selected_file = file
        
    def _compute_diff(self, old_lines, new_lines):
        hunks = []
        current_hunk = None
        max_len = max(len(old_lines), len(new_lines))
        for i in range(max_len):
            old_line = old_lines[i] if i < len(old_lines) else None
            new_line = new_lines[i] if i < len(new_lines) else None
            if old_line == new_line:
                if current_hunk:
                    current_hunk.lines.append(DiffLine(content=old_line or "", line_type=DiffLineType.EQUAL, old_line_num=i + 1, new_line_num=i + 1))
            else:
                if current_hunk is None:
                    current_hunk = DiffHunk(header="@@ -" + str(i+1) + " +" + str(i+1) + " @")
                    hunks.append(current_hunk)
                if old_line is not None:
                    current_hunk.lines.append(DiffLine(content=old_line, line_type=DiffLineType.REMOVE, old_line_num=i + 1))
                if new_line is not None:
                    current_hunk.lines.append(DiffLine(content=new_line, line_type=DiffLineType.ADD, new_line_num=i + 1))
        return hunks
        
    def select_file(self, index):
        if 0 <= index < len(self.files):
            self.selected_file = self.files[index]
            return self.selected_file
        return None
        
    def set_view_mode(self, mode):
        self.view_mode = mode
        
    def get_statistics(self):
        total_add = sum(f.additions for f in self.files)
        total_del = sum(f.deletions for f in self.files)
        return {"files": len(self.files), "additions": total_add, "deletions": total_del, "changes": total_add + total_del}
