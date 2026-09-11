"""
Safety constraint test: agent/ must NOT import repositories/ or supabase_client.

This is the core architectural guarantee of the project — the agent
can only act through the service layer. If this test fails, someone
added a direct import that bypasses business logic.
"""

import ast
import os
import pytest


AGENT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "app", "agent"
)

FORBIDDEN_IMPORTS = [
    "app.repositories",
    "app.core.supabase_client",
]


def get_python_files(directory: str) -> list[str]:
    """Return all .py files in the directory."""
    files = []
    for fname in os.listdir(directory):
        if fname.endswith(".py") and fname != "__init__.py":
            files.append(os.path.join(directory, fname))
    return files


def get_imports_from_file(filepath: str) -> list[str]:
    """Parse a Python file and return all imported module names."""
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


class TestAgentSafety:
    def test_agent_does_not_import_repositories(self):
        """agent/ files must not import from app.repositories."""
        for filepath in get_python_files(AGENT_DIR):
            imports = get_imports_from_file(filepath)
            for imp in imports:
                for forbidden in FORBIDDEN_IMPORTS:
                    assert not imp.startswith(forbidden), (
                        f"SAFETY VIOLATION: {os.path.basename(filepath)} "
                        f"imports '{imp}' — agent must only use services/"
                    )
