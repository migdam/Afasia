"""Every backend dependency is pinned to an exact version."""
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", ["requirements.txt", "requirements-dev.txt"])
def test_requirements_are_pinned(name):
    lines = (BACKEND / name).read_text().splitlines()
    requirements = [line.split("#")[0].strip() for line in lines]
    unpinned = [r for r in requirements if r and "==" not in r]
    assert not unpinned, f"{name}: pin these with ==: {unpinned}"


def test_the_node_tools_are_pinned_and_locked():
    """ESLint and its parts (backlog P3-3a): exact versions, and a lockfile
    for everything they bring."""
    import json

    root = BACKEND.parent
    tools = json.loads((root / "package.json").read_text())["devDependencies"]
    unpinned = [f"{name}@{version}" for name, version in tools.items() if not version[0].isdigit()]

    assert tools and not unpinned, f"pin these exactly: {unpinned}"
    assert set(tools) <= set(json.loads((root / "package-lock.json").read_text())["packages"][""]["devDependencies"])
