from __future__ import annotations

from typing import Any


def ci_cd_template() -> dict[str, Any]:
    return {
        "metadata": {"name": "CI/CD Pipeline", "description": "Build, test, deploy, and health check"},
        "nodes": [
            {
                "id": "build",
                "type": "SHELL",
                "name": "Build Application",
                "config": {"command": "docker build -t app:latest .", "timeout": 600},
            },
            {
                "id": "test",
                "type": "SHELL",
                "name": "Run Tests",
                "config": {"command": "pytest tests/ --coverage", "timeout": 300},
            },
            {
                "id": "condition",
                "type": "CONDITION",
                "name": "Tests Passed?",
                "config": {"expression": "test_success == True"},
            },
            {
                "id": "deploy",
                "type": "HTTP",
                "name": "Deploy to Production",
                "config": {
                    "url": "https://api.example.com/deploy",
                    "method": "POST",
                    "headers": {"Authorization": "Bearer $deploy_token"},
                    "timeout": 120,
                },
            },
            {
                "id": "health_check",
                "type": "HTTP",
                "name": "Health Check",
                "config": {"url": "https://app.example.com/health", "method": "GET", "timeout": 30},
            },
            {
                "id": "notify",
                "type": "TOOL",
                "name": "Send Notification",
                "config": {"tool_name": "slack_notify", "params": {"channel": "#deployments"}},
            },
        ],
        "edges": [
            {"source": "build", "target": "test"},
            {"source": "test", "target": "condition"},
            {"source": "condition", "target": "deploy", "condition": "condition_result == True"},
            {"source": "condition", "target": "notify", "condition": "condition_result == False"},
            {"source": "deploy", "target": "health_check"},
            {"source": "health_check", "target": "notify"},
        ],
    }
