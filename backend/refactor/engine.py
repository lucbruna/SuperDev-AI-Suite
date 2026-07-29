from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/refactor", tags=["refactor"])


@router.post("/analyze")
async def analyze_files(filepaths: list[str]) -> dict[str, Any]:
    files = []
    for fp in filepaths:
        fp = fp.strip()
        if not os.path.exists(fp):
            for dirpath, _, filenames in os.walk("."):
                if fp in filenames:
                    fp = os.path.join(dirpath, fp)
                    break
        if not os.path.exists(fp):
            raise HTTPException(status_code=404, detail=f"File not found: {fp}")
        with open(fp, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        files.append({"path": fp, "content": content, "lines": content.count("\n") + 1, "size": len(content)})
    return {"files": files, "total": len(files)}


@router.post("/edit")
async def multi_file_edit(edits: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    for edit in edits:
        filepath = edit.get("filepath", "")
        old_string = edit.get("old_string", "")
        new_string = edit.get("new_string", "")

        if not os.path.exists(filepath):
            results.append({"filepath": filepath, "status": "error", "error": "File not found"})
            continue

        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if old_string not in content:
            results.append({"filepath": filepath, "status": "error", "error": "String not found"})
            continue

        new_content = content.replace(old_string, new_string, 1)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        results.append({"filepath": filepath, "status": "edited", "changes": 1})

    return {"results": results, "total": len(results), "successful": sum(1 for r in results if r["status"] == "edited")}


@router.post("/search-replace")
async def search_replace(body: dict[str, Any]) -> dict[str, Any]:
    filepath = body.get("filepath", "")
    search = body.get("search", "")
    replace = body.get("replace", "")
    if not filepath or not search:
        return {"success": False, "error": "filepath and search are required"}
    if not os.path.exists(filepath):
        return {"success": False, "error": "File not found"}
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if search not in content:
        return {"success": False, "error": "String not found"}
    occurrences = content.count(search)
    new_content = content.replace(search, replace)
    if not body.get("dry_run"):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
    return {"success": True, "filepath": filepath, "occurrences": occurrences, "preview": new_content[:500] if body.get("dry_run") else None}


@router.post("/rename-symbol")
async def rename_symbol_body(body: dict[str, Any]) -> dict[str, Any]:
    filepath = body.get("filepath", "")
    old_name = body.get("old_name", "")
    new_name = body.get("new_name", "")
    if not filepath or not old_name or not new_name:
        return {"success": False, "error": "filepath, old_name, and new_name are required"}
    if not os.path.exists(filepath):
        return {"success": False, "error": "File not found"}
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if old_name not in content:
        return {"success": False, "error": f"Symbol '{old_name}' not found"}
    new_content = content.replace(old_name, new_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    count = content.count(old_name)
    return {"success": True, "filepath": filepath, "old_name": old_name, "new_name": new_name, "occurrences_replaced": count}


@router.post("/rename")
async def rename_symbol(filepath: str, old_name: str, new_name: str) -> dict[str, Any]:
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    if old_name not in content:
        raise HTTPException(status_code=400, detail=f"Symbol '{old_name}' not found in file")
    new_content = content.replace(old_name, new_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    count = content.count(old_name)
    return {"filepath": filepath, "old_name": old_name, "new_name": new_name, "occurrences_replaced": count}


@router.post("/extract-function")
async def extract_function(body: dict[str, Any]) -> dict[str, Any]:
    filepath = body.get("filepath", "")
    function_name = body.get("new_function_name") or body.get("function_name", "")
    start_line = body.get("start_line", 1)
    end_line = body.get("end_line", 10)
    if not filepath:
        return {"success": False, "error": "filepath is required"}
    if not os.path.exists(filepath):
        return {"success": False, "error": "File not found"}
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    if start_line < 1 or end_line > len(lines):
        return {"success": False, "error": f"Line range {start_line}-{end_line} out of bounds (file has {len(lines)} lines)"}
    extracted = "".join(lines[start_line - 1 : end_line])
    new_function = f"\ndef {function_name}():\n{extracted}\n"
    lines.insert(end_line, new_function)
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return {"success": True, "filepath": filepath, "function_name": function_name, "extracted_lines": end_line - start_line + 1, "new_file_lines": len(lines)}