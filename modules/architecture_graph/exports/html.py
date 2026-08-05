"""Self-contained interactive HTML export (no external dependencies).

Embeds the graph as static JSON plus a small vanilla-JS canvas with pan/zoom
and layer filtering — works by simply opening the file in a browser.
"""
from __future__ import annotations

import html as html_lib
import json
from typing import Any

from modules.architecture_graph.exports.reactflow import _KIND_COLOR, to_reactflow
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Architecture Graph — {title}</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:#0f172a; color:#e2e8f0; }}
  header {{ padding:12px 20px; border-bottom:1px solid #1e293b; display:flex; gap:16px; align-items:center; flex-wrap:wrap; }}
  header h1 {{ font-size:16px; margin:0; }}
  .legend {{ display:flex; gap:12px; flex-wrap:wrap; font-size:12px; color:#94a3b8; }}
  .legend span {{ display:inline-flex; align-items:center; gap:4px; }}
  .dot {{ width:10px; height:10px; border-radius:2px; display:inline-block; }}
  #canvas {{ width:100vw; height:calc(100vh - 64px); overflow:hidden; position:relative; cursor:grab; }}
  #canvas.dragging {{ cursor:grabbing; }}
  svg {{ position:absolute; top:0; left:0; }}
  .node text {{ fill:#e2e8f0; font-size:11px; font-family:inherit; }}
  .edge {{ stroke:#94a3b8; stroke-width:1.2; fill:none; marker-end:url(#arrow); }}
  .edge-label {{ fill:#64748b; font-size:9px; }}
  #tooltip {{ position:fixed; display:none; background:#1e293b; border:1px solid #334155; border-radius:8px; padding:10px 12px; font-size:12px; max-width:320px; z-index:10; }}
  #tooltip b {{ display:block; margin-bottom:4px; }}
</style>
</head>
<body>
<header>
  <h1>Architecture Graph — {title}</h1>
  <div class="legend" id="legend"></div>
</header>
<div id="canvas"></div>
<div id="tooltip"></div>
<svg width="0" height="0" style="position:absolute"><defs>
  <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
    <path d="M0,0 L0,6 L7,3 z" fill="#94a3b8"/>
  </marker>
</defs></svg>
<script>
const DATA = {data};
const KIND_COLORS = {colors};
const W = 1600, H = 1000;
const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
svg.setAttribute("width", W); svg.setAttribute("height", H);
document.getElementById("canvas").appendChild(svg);

// Layer bands
const byLayer = {{}};
DATA.nodes.forEach(n => {{ (byLayer[n.data.layer || "unknown"] = byLayer[n.data.layer || "unknown"] || []).push(n); }});

// Edges
DATA.edges.forEach(e => {{
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.classList.add("edge");
  line.setAttribute("x1", srcX(e)); line.setAttribute("y1", srcY(e));
  line.setAttribute("x2", dstX(e)); line.setAttribute("y2", dstY(e));
  svg.appendChild(line);
}});

function srcX(e) {{ return nodeById(e.source).position.x + 60; }}
function srcY(e) {{ return nodeById(e.source).position.y + 12; }}
function dstX(e) {{ return nodeById(e.target).position.x + 60; }}
function dstY(e) {{ return nodeById(e.target).position.y + 12; }}
const nodeMap = {{}}; DATA.nodes.forEach(n => nodeMap[n.id] = n);
function nodeById(id) {{ return nodeMap[id]; }}

// Nodes
DATA.nodes.forEach(n => {{
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  g.classList.add("node");
  g.setAttribute("transform", `translate(${{n.position.x}}, ${{n.position.y}})`);
  const color = KIND_COLORS[n.data.kind] || "#94a3b8";
  const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
  rect.setAttribute("width", 120); rect.setAttribute("height", 24);
  rect.setAttribute("rx", 6);
  rect.setAttribute("fill", color + "22"); rect.setAttribute("stroke", color);
  const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
  text.setAttribute("x", 60); text.setAttribute("y", 15); text.setAttribute("text-anchor", "middle");
  text.textContent = (n.data.label || n.id).slice(0, 22);
  g.appendChild(rect); g.appendChild(text);
  g.addEventListener("mouseenter", () => showTip(n, event));
  g.addEventListener("mousemove", (e) => moveTip(e));
  g.addEventListener("mouseleave", hideTip);
  svg.appendChild(g);
}});

function showTip(n, ev) {{
  const tip = document.getElementById("tooltip");
  tip.innerHTML = `<b>${{n.data.label}}</b><div>id: ${{n.id}}</div><div>kind: ${{n.data.kind}} · layer: ${{n.data.layer || "?"}}</div><div style="color:#64748b">${{n.data.path || ""}}</div>`;
  tip.style.display = "block";
  moveTip(ev);
}}
function moveTip(e) {{ const tip = document.getElementById("tooltip"); tip.style.left = (e.clientX + 14) + "px"; tip.style.top = (e.clientY + 14) + "px"; }}
function hideTip() {{ document.getElementById("tooltip").style.display = "none"; }}

// Pan & zoom
let tx = 0, ty = 0, scale = 0.7;
function render() {{ svg.setAttribute("transform", `translate(${{tx}}, ${{ty}}) scale(${{scale}})`); }}
render();
const canvas = document.getElementById("canvas");
let dragging = false, sx = 0, sy = 0;
canvas.addEventListener("mousedown", e => {{ dragging = true; canvas.classList.add("dragging"); sx = e.clientX - tx; sy = e.clientY - ty; }});
window.addEventListener("mousemove", e => {{ if (dragging) {{ tx = e.clientX - sx; ty = e.clientY - sy; render(); }} }});
window.addEventListener("mouseup", () => {{ dragging = false; canvas.classList.remove("dragging"); }});
canvas.addEventListener("wheel", e => {{ e.preventDefault(); scale = Math.min(2.5, Math.max(0.2, scale * (e.deltaY < 0 ? 1.1 : 0.9))); render(); }}, {{ passive:false }});

// Legend
const seen = new Set();
DATA.nodes.forEach(n => {{
  if (!seen.has(n.data.kind)) {{
    seen.add(n.data.kind);
    const el = document.createElement("span");
    el.innerHTML = `<span class="dot" style="background:${{KIND_COLORS[n.data.kind] || "#94a3b8"}}"></span>${{n.data.kind}}`;
    document.getElementById("legend").appendChild(el);
  }}
}});
</script>
</body>
</html>
"""


def to_html(graph: ArchitectureGraph, title: str = "superdev") -> str:
    data = to_reactflow(graph)
    colors = json.dumps(_KIND_COLOR)
    payload = json.dumps(data, ensure_ascii=False)
    return _TEMPLATE.format(
        title=html_lib.escape(title),
        data=payload,
        colors=colors,
    )


def to_dict(graph: ArchitectureGraph, title: str = "superdev") -> dict[str, Any]:
    return {"format": "html", "source": to_html(graph, title)}
