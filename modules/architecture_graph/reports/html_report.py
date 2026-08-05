"""HTML report: styled, self-contained rendering of the architecture report.

Embeds the markdown report converted to simple HTML plus an embedded Mermaid
graph. Zero external assets — safe to email or store offline.
"""
from __future__ import annotations

import html as html_lib
import re
from typing import Any

from modules.architecture_graph.exports.mermaid import to_mermaid
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.reports.architecture_report import (
    ArchitectureReport,
)

_MARKDOWN_RE = re.compile(r"^(#{1,4})\s+(.*)$")
_LIST_RE = re.compile(r"^\s*[-*]\s+(.*)$")
_HR_RE = re.compile(r"^---+$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_CODE_RE = re.compile(r"`([^`]+)`")


def _inline(text: str) -> str:
    text = html_lib.escape(text)
    text = _BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = _CODE_RE.sub(r"<code>\1</code>", text)
    return text


def _md_to_html(markdown: str) -> str:
    """Very small markdown -> HTML converter for the report subset."""
    lines = markdown.splitlines()
    out: list[str] = []
    in_list = False
    in_table = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            out.append("</table>")
            in_table = False

    for line in lines:
        stripped = line.strip()
        heading = _MARKDOWN_RE.match(line)
        if heading:
            close_list(); close_table()
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2).strip())}</h{level}>")
        elif stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                out.append("<table>")
                in_table = True
            tag = "th" if all(c.startswith("-") or c == "" for c in cells) else "td"
            row = "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells)
            if tag == "th":
                continue  # separator row
            out.append(f"<tr>{row}</tr>")
        elif (list_match := _LIST_RE.match(line)):
            close_table()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(list_match.group(1))}</li>")
        elif _HR_RE.match(stripped):
            close_list(); close_table()
            out.append("<hr/>")
        elif stripped == "":
            close_list()
        else:
            close_list(); close_table()
            out.append(f"<p>{_inline(stripped)}</p>")

    close_list(); close_table()
    return "\n".join(out)


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:#0f172a; color:#e2e8f0; line-height:1.6; }}
  main {{ max-width: 900px; margin: 0 auto; padding: 32px 24px 80px; }}
  h1 {{ border-bottom: 1px solid #334155; padding-bottom: 8px; }}
  h2, h3, h4 {{ margin-top: 28px; color: #94a3b8; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ border: 1px solid #334155; padding: 6px 10px; text-align: left; font-size: 14px; }}
  th {{ background: #1e293b; }}
  code {{ background: #1e293b; padding: 1px 6px; border-radius: 4px; font-size: 13px; }}
  strong {{ color: #fbbf24; }}
  ul {{ margin: 8px 0; }}
  hr {{ border: none; border-top: 1px solid #334155; margin: 20px 0; }}
  .mermaid-wrap {{ margin-top: 24px; }}
  .mermaid-wrap summary {{ cursor: pointer; color: #60a5fa; }}
  #graph {{ max-width: 100%; overflow-x: auto; background: #0b1220; border-radius: 8px; padding: 12px; }}
  pre.mermaid {{ font-family: monospace; font-size: 11px; white-space: pre-wrap; color: #7dd3fc; }}
</style>
</head>
<body>
<main>
{body}
<details class="mermaid-wrap">
  <summary>View Mermaid source</summary>
  <div id="graph"><pre class="mermaid">{mermaid}</pre></div>
</details>
</main>
</body>
</html>
"""


def to_html_report(graph: ArchitectureGraph, title: str = "Architecture Report") -> str:
    markdown = ArchitectureReport().generate(graph)
    body = _md_to_html(markdown)
    mermaid = html_lib.escape(to_mermaid(graph))
    return _TEMPLATE.format(
        title=html_lib.escape(title),
        body=body,
        mermaid=mermaid,
    )


def to_dict(graph: ArchitectureGraph, title: str = "Architecture Report") -> dict[str, Any]:
    return {"format": "html", "title": title, "source": to_html_report(graph, title)}


def write_html_report(graph: ArchitectureGraph, path: str, title: str = "Architecture Report") -> dict[str, Any]:
    from pathlib import Path

    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(to_html_report(graph, title), encoding="utf-8")
    return {"path": str(dest), "bytes": dest.stat().st_size}
