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
