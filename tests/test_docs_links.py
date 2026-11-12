"""Every relative Markdown link in the repo must resolve to an existing file.

Code spans and fenced code blocks are ignored, so link examples in them don't count.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "node_modules", "dist", ".mypy_cache", ".pytest_cache", ".ruff_cache"}

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,}).*?^ {0,3}\1[^\n]*$", re.DOTALL | re.MULTILINE)
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1", re.DOTALL)
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts)
        and "tests/fixtures/local" not in path.relative_to(ROOT).as_posix()
    )


def relative_links(text: str) -> list[str]:
    text = FENCE.sub("", text)
    text = CODE_SPAN.sub("", text)
    links = []
    for match in LINK.finditer(text):
        target = match.group(1)
        if SCHEME.match(target) or target.startswith("#"):
            continue
        links.append(target)
    return links


def broken_links(path: Path) -> list[str]:
    return [
        target
        for target in relative_links(path.read_text(encoding="utf-8"))
        if not (path.parent / target.split("#", 1)[0]).exists()
    ]


def test_finds_markdown_files() -> None:
    assert len(markdown_files()) > 10


@pytest.mark.parametrize("path", markdown_files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_relative_links_resolve(path: Path) -> None:
    assert broken_links(path) == []


def test_ignores_code_and_external_links() -> None:
    text = (
        "[ok](https://example.com) [anchor](#top) `[x](missing.md)`\n"
        "```\n[y](missing.md)\n```\n[z](real.md#part)\n"
    )
    assert relative_links(text) == ["real.md#part"]


def test_detects_broken_link(tmp_path: Path) -> None:
    (tmp_path / "there.md").write_text("x", encoding="utf-8")
    doc = tmp_path / "doc.md"
    doc.write_text("[a](there.md) [b](gone.md)", encoding="utf-8")
    assert broken_links(doc) == ["gone.md"]
