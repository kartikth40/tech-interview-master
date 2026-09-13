"""Auto-generate the DSA "Code Library" pages at build time.

Walks DSA/{patterns,algorithms,data-structures} for .py files and produces three
virtual Markdown pages that embed each file as a highlighted code block via
pymdownx.snippets (`--8<--`). New .py files appear on the site with zero manual edits.

Run automatically by the mkdocs-gen-files plugin (see mkdocs.yml). The generated
pages are virtual: they are NOT written into the repo.
"""

from pathlib import Path

import mkdocs_gen_files

# Repo root = parent of this scripts/ dir.
ROOT = Path(__file__).resolve().parent.parent

SKIP = {"sample.py"}


def title_from_filename(path: Path) -> str:
    """sliding_window.py -> 'Sliding Window'."""
    return path.stem.replace("_", " ").title()


def group_title(name: str) -> str:
    return name.replace("-", " ").title()


def collect(rel_dir: str) -> dict[str, list[Path]]:
    """Return {subgroup_label: [py files]} under DSA/<rel_dir>, sorted."""
    base = ROOT / "DSA" / rel_dir
    groups: dict[str, list[Path]] = {}
    for py in sorted(base.rglob("*.py")):
        if py.name in SKIP or "__pycache__" in py.parts:
            continue
        # subgroup = immediate folder under base, or the base itself if flat
        rel = py.relative_to(base)
        subgroup = rel.parts[0] if len(rel.parts) > 1 else ""
        groups.setdefault(subgroup, []).append(py)
    return groups


def render_page(out_path: str, heading: str, intro: str, rel_dir: str) -> None:
    groups = collect(rel_dir)
    with mkdocs_gen_files.open(out_path, "w") as f:
        f.write(f"# {heading}\n\n{intro}\n\n")
        f.write("> Use the copy button on any block to grab the code. "
                "These embed the real source files, so they always match the repo.\n\n")
        for subgroup in sorted(groups):
            if subgroup:
                f.write(f"## {group_title(subgroup)}\n\n")
            for py in groups[subgroup]:
                snippet_path = py.relative_to(ROOT).as_posix()
                level = "###" if subgroup else "##"
                f.write(f"{level} {title_from_filename(py)}\n\n")
                f.write('```python linenums="1"\n')
                f.write(f'--8<-- "{snippet_path}"\n')
                f.write("```\n\n")


render_page(
    "DSA/code-library/patterns.md",
    "DSA Patterns — Code Library",
    "Runnable Python implementations of the core interview patterns. "
    "Each file has a header (difficulty, when-to-use, common mistakes) and a `__main__` demo. "
    "Source lives in `DSA/patterns/`.",
    "patterns",
)

render_page(
    "DSA/code-library/algorithms.md",
    "DSA Algorithms — Code Library",
    "Runnable Python implementations of core algorithms, grouped by domain. "
    "Source lives in `DSA/algorithms/`.",
    "algorithms",
)

render_page(
    "DSA/code-library/data-structures.md",
    "DSA Data Structures — Code Library",
    "Runnable Python implementations of the data structures worth knowing by heart. "
    "Source lives in `DSA/data-structures/`.",
    "data-structures",
)

