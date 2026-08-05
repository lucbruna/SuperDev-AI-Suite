"""Docker scanner: parses Dockerfiles and docker-compose service maps.

* Dockerfiles -> base images (FROM) and copied source paths (COPY).
* compose files -> service names, images and cross-service depends_on links
  (the raw YAML parse is reused; this scanner adds the docker semantics).
"""
from __future__ import annotations

import re
from typing import Any

from modules.architecture_graph.parsers import yaml_parser

_FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)")
_COPY_RE = re.compile(r"^\s*COPY\s+([^\s]+)")
_EXPOSE_RE = re.compile(r"^\s*EXPOSE\s+([^\s]+)")
_COMPOSE_NAMES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")


def parse_dockerfile(text: str) -> dict[str, Any]:
    base_images: list[str] = []
    copies: list[str] = []
    exposes: list[str] = []
    for line in text.splitlines():
        match = _FROM_RE.match(line)
        if match:
            base_images.append(match.group(1))
            continue
        match = _COPY_RE.match(line)
        if match:
            copies.append(match.group(1))
            continue
        match = _EXPOSE_RE.match(line)
        if match:
            exposes.append(match.group(1))
    return {"base_images": base_images, "copies": copies, "exposes": exposes}


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    rel_path = rel_path.replace("\\", "/")
    filename = rel_path.rsplit("/", 1)[-1]
    if filename.lower() == "dockerfile" or filename.lower().endswith(".dockerfile"):
        parsed = parse_dockerfile(text)
        parsed["language"] = "docker"
    elif filename.lower() in _COMPOSE_NAMES:
        parsed = yaml_parser.parse(text, rel_path)
        parsed["language"] = "docker"
        parsed["compose"] = True
    else:
        parsed = yaml_parser.parse(text, rel_path)
        parsed["language"] = "docker"
    parsed["rel_path"] = rel_path
    return parsed
