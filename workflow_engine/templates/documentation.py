from __future__ import annotations

from typing import Any


def documentation_template() -> dict[str, Any]:
    return {
        "metadata": {"name": "Documentation Pipeline", "description": "Analyze code, generate docs, review, and publish"},
        "nodes": [
            {
                "id": "analyze",
                "type": "PYTHON",
                "name": "Analyze Source Code",
                "config": {
                    "code": "import ast\nimport os\n\ncontext['modules'] = []\nfor root, dirs, files in os.walk('src'):\n    for f in files:\n        if f.endswith('.py'):\n            context['modules'].append(os.path.join(root, f))\nresult = {'module_count': len(context['modules'])}",
                    "imports": ["import ast", "import os"],
                },
            },
            {
                "id": "generate",
                "type": "AGENT",
                "name": "Generate Documentation",
                "config": {"agent_name": "docs_writer", "task": "Generate markdown documentation from source", "model": "gpt-4"},
            },
            {
                "id": "review",
                "type": "TOOL",
                "name": "Review Documentation",
                "config": {"tool_name": "doc_reviewer", "params": {"strict": True}},
            },
            {
                "id": "publish",
                "type": "HTTP",
                "name": "Publish Docs",
                "config": {"url": "https://docs.example.com/api/publish", "method": "POST", "timeout": 60},
            },
        ],
        "edges": [
            {"source": "analyze", "target": "generate"},
            {"source": "generate", "target": "review"},
            {"source": "review", "target": "publish"},
        ],
    }
