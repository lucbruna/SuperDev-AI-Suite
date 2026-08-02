"""Skill documentation — renders Markdown docs for a skill definition."""
from __future__ import annotations

from modules.ai_video_studio.skills.skill_registry import SkillDefinition


def generate_documentation(definition: SkillDefinition) -> str:
    """Return a Markdown reference card for a skill definition."""
    tags = ", ".join(definition.tags) or "—"
    permissions = ", ".join(definition.permissions) or "none"
    entrypoint = "async __call__(**kwargs)" if definition.entrypoint else "none"
    metadata_lines = "".join(
        f"- `{k}`: {v}\n" for k, v in sorted(definition.metadata.items())
    ) or "—"
    return f"""# {definition.name}

`{definition.id}` v{definition.version} · category `{definition.category}`

{definition.description or "_No description._"}

## Details

- **Tags:** {tags}
- **Permissions:** {permissions}
- **Entrypoint:** {entrypoint}

## Metadata

{metadata_lines}

## Example

```python
from modules.ai_video_studio.skills.skill_engine import get_skill_engine

result = await get_skill_engine().run("{definition.id}", {{}}, **{{}})
print(result.output)
```
"""
