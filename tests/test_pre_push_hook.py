import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".githooks" / "pre-push"
ZERO = "0" * 40
SHA = "1" * 40


def run_hook(*remote_refs: str) -> subprocess.CompletedProcess[str]:
    stdin = "".join(f"refs/heads/topic {SHA} {ref} {ZERO}\n" for ref in remote_refs)
    return subprocess.run(
        ["sh", str(HOOK), "origin", "https://example.invalid/repo.git"],
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_hook_is_executable() -> None:
    assert HOOK.stat().st_mode & 0o111


def test_rejects_push_to_main() -> None:
    result = run_hook("refs/heads/main")
    assert result.returncode != 0
    assert "main" in result.stderr


def test_rejects_main_among_other_refs() -> None:
    assert run_hook("refs/heads/chore/x", "refs/heads/main").returncode != 0


@pytest.mark.parametrize(
    "ref",
    [
        "refs/heads/chore/bootstrap",
        "refs/heads/feature/main",
        "refs/heads/mainline",
        "refs/tags/v0.1.0",
    ],
)
def test_allows_other_refs(ref: str) -> None:
    assert run_hook(ref).returncode == 0


def test_allows_empty_push() -> None:
    assert run_hook().returncode == 0
