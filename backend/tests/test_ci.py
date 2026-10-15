"""Continuous integration runs the checks on every push and pull request
(backlog P3-2, gate G13)."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "checks.yml"


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def steps(job):
    return workflow()["jobs"][job]["steps"]


def test_it_runs_on_every_push_and_pull_request():
    # YAML reads the key "on" as True.
    triggers = workflow()[True]

    assert "push" in triggers and "pull_request" in triggers
    assert not triggers["push"]  # every branch, no filter


def test_it_runs_the_full_check_and_the_docker_smoke_test():
    assert any(line.strip().startswith("scripts/check.sh")
               for step in steps("check") for line in step.get("run", "").splitlines())
    assert any(line.strip().startswith("scripts/docker-smoke.sh")
               for step in steps("docker") for line in step.get("run", "").splitlines())


def test_it_uses_the_python_of_the_docker_image():
    python = next(step["with"]["python-version"] for step in steps("check")
                  if step.get("uses", "").startswith("actions/setup-python@"))
    dockerfile = (ROOT / "backend" / "Dockerfile").read_text()

    assert f"FROM python:{python}-slim" in dockerfile


def test_actions_are_pinned_to_commits_and_can_only_read():
    uses = [step["uses"] for job in workflow()["jobs"] for step in steps(job) if "uses" in step]

    assert uses and all(re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", ref) for ref in uses), uses
    assert workflow()["permissions"] == {"contents": "read"}
