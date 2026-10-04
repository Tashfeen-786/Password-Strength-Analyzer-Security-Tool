"""Write a clean project-structure listing to evidence/project_structure.txt."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"node_modules", "dist", "__pycache__", ".pytest_cache", ".venv",
        "venv", ".git", "analytics.db", "pdf_full_text.txt", "package-lock.json"}
MAX_DEPTH = 3


def render(dir_path: Path, prefix: str = "", depth: int = 0) -> list[str]:
    if depth > MAX_DEPTH:
        return []
    entries = sorted(e for e in dir_path.iterdir() if e.name not in SKIP)
    lines = []
    for i, entry in enumerate(entries):
        last = i == len(entries) - 1
        connector = "└── " if last else "├── "
        lines.append(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))
        if entry.is_dir():
            ext = "    " if last else "│   "
            lines += render(entry, prefix + ext, depth + 1)
    return lines


def main() -> None:
    out = ROOT / "evidence" / "project_structure.txt"
    out.parent.mkdir(exist_ok=True)
    lines = [ROOT.name + "/"] + render(ROOT)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
