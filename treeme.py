#!/usr/bin/env python3
"""
Create a directory tree (tree.txt) and concatenate selected files (all_texts.txt).

Features:
- Auto-excludes: .git, .idea, .venv, venv
- CLI flags for extra excludes, ignore globs, output filenames, root dir, extensions,
  and specific filenames to include.

Usage:
  python make_tree_and_bundle.py \
    --exclude node_modules,__pycache__ \
    --ignore "*.min.js,*.map" \
    --exts ".txt,.sh,.py,.sql" \
    --include-names "Dockerfile,README" \
    --out tree.txt \
    --bundle all_texts.txt \
    --root .

Notes:
- Ignore patterns apply to BOTH the tree view and the bundle.
- Extensions are matched case-insensitively and should be given with leading dots.
"""

from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path
from typing import Iterable, List, Set

AUTO_EXCLUDES = {".git", ".idea", ".venv", "venv"}
DEFAULT_EXTS = {".txt", ".sh", ".py", ".sql"}


def parse_csv_set(s: str) -> Set[str]:
    if not s:
        return set()
    return {part.strip() for part in s.split(",") if part.strip()}


def normalized_exts(csv_exts: str | None) -> Set[str]:
    if not csv_exts:
        return set(DEFAULT_EXTS)
    exts = {e.strip() for e in csv_exts.split(",") if e.strip()}
    # Ensure each has a leading dot; store lowercase
    return {e if e.startswith(".") else f".{e}".lower() for e in exts}


def matches_any_glob(path: Path, patterns: Iterable[str], root: Path) -> bool:
    if not patterns:
        return False
    rel = path.relative_to(root)
    name = path.name
    rel_posix = rel.as_posix()
    # Match against filename and the relative path
    for pat in patterns:
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(rel_posix, pat):
            return True
    return False


def build_tree_and_collect_files(
    root: Path,
    excludes: Set[str],
    ignore_globs: Set[str],
    allowed_exts: Set[str],
    include_names: Set[str],  # <--- ADDED
    tree_output: Path,
    bundle_output: Path,
) -> List[Path]:
    """
    Walk `root`, write a tree to `tree_output`, and return list of files (relative paths)
    to include in bundle (by extension). Applies folder excludes and glob ignores to both
    tree and bundle. Skips the output files themselves.
    """
    lines: List[str] = []
    collected: List[Path] = []
    skip_names = {tree_output.name, bundle_output.name}

    def _walk(dir_path: Path, prefix: str = ""):
        try:
            entries = sorted(
                (p for p in dir_path.iterdir() if not p.is_symlink()),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            lines.append(prefix + "└── [permission denied]")
            return
        except FileNotFoundError:
            return

        # Filter out excluded/ignored dirs (by name or glob)
        visible = []
        for p in entries:
            if p.is_dir():
                if p.name in excludes:
                    continue
                if matches_any_glob(p, ignore_globs, root):
                    continue
                visible.append(p)
            else:
                # Files: skip if match ignore globs or are our outputs
                if p.name in skip_names:
                    continue
                if matches_any_glob(p, ignore_globs, root):
                    continue
                visible.append(p)

        total = len(visible)
        for idx, p in enumerate(visible):
            is_last = idx == total - 1
            branch = "└── " if is_last else "├── "
            display = p.name + ("/" if p.is_dir() else "")
            lines.append(prefix + branch + display)

            if p.is_dir():
                _walk(p, prefix + ("    " if is_last else "│   "))
            else:
                # <--- MODIFIED THIS BLOCK
                if p.suffix.lower() in allowed_exts or p.name in include_names:
                    collected.append(p.relative_to(root))

    lines.append(root.resolve().name + "/")
    _walk(root)

    tree_output.write_text("\n".join(lines), encoding="utf-8")
    return collected


def write_bundle(root: Path, files: List[Path], bundle_output: Path) -> None:
    with bundle_output.open("w", encoding="utf-8", errors="replace") as out:
        for rel in files:
            abs_path = root / rel
            out.write("\n\n")
            out.write("=" * 80 + "\n")
            out.write(f"FILE: {rel.as_posix()}\n")
            out.write("=" * 80 + "\n")
            try:
                text = abs_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                out.write(f"[ERROR READING FILE: {e}]\n")
                continue
            out.write(text)


def main():
    ap = argparse.ArgumentParser(description="Create a tree and bundle files.")
    ap.add_argument("--root", default=".", help="Root directory to scan (default: current directory).")
    ap.add_argument("--exclude", default="", help="Comma-separated folder names to exclude at any depth.")
    ap.add_argument("--ignore", default="", help="Comma-separated glob patterns to ignore (files/dirs). Example: \"*.min.js,*.map,build*\"")
    ap.add_argument("--exts", default=".txt,.sh,.py,.sql", help="Comma-separated file extensions to include in the bundle (with dots).")
    ap.add_argument("--include-names", default="", help="Comma-separated exact filenames to include (e.g., 'Dockerfile,README').")  # <--- ADDED
    ap.add_argument("--out", dest="tree_out", default="tree.txt", help="Output file for the tree (default: tree.txt).")
    ap.add_argument("--bundle", dest="bundle_out", default="all_texts.txt", help="Output file for the concatenated contents (default: all_texts.txt).")

    args = ap.parse_args()

    root = Path(args.root).resolve()
    tree_out = Path(args.tree_out)
    bundle_out = Path(args.bundle_out)

    excludes = AUTO_EXCLUDES | parse_csv_set(args.exclude)
    ignore_globs = parse_csv_set(args.ignore)
    allowed_exts = {e.lower() for e in normalized_exts(args.exts)}
    include_names = parse_csv_set(args.include_names)  # <--- ADDED

    print(f"Root: {root}")
    print(f"Tree file: {tree_out}")
    print(f"Bundle file: {bundle_out}")
    print(f"Auto excludes: {', '.join(sorted(AUTO_EXCLUDES)) or '(none)'}")
    extra_ex = sorted(parse_csv_set(args.exclude))
    print(f"Extra excludes: {', '.join(extra_ex) if extra_ex else '(none)'}")
    print(f"Ignore globs: {', '.join(sorted(ignore_globs)) if ignore_globs else '(none)'}")
    print(f"Extensions: {', '.join(sorted(allowed_exts))}")
    print_inc_names = sorted(include_names)  # <--- ADDED
    print(f"Include names: {', '.join(print_inc_names) if print_inc_names else '(none)'}")  # <--- ADDED

    collected = build_tree_and_collect_files(
        root=root,
        excludes=excludes,
        ignore_globs=ignore_globs,
        allowed_exts=allowed_exts,
        include_names=include_names,  # <--- ADDED
        tree_output=tree_out,
        bundle_output=bundle_out,
    )
    print(f"Collected {len(collected)} file(s) for bundling.")
    write_bundle(root, collected, bundle_out)
    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")