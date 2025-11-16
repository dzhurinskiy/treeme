# treeme

Create a clean ASCII file tree and a single “bundle” file with the contents of selected source/text files — perfect for code reviews, audits, or sharing a snapshot of your project.

- Writes a tree to `tree.txt`.
- Concatenates the contents of matching files (e.g., `.txt`, `.sh`, `.py`, `.sql`) into `all_texts.txt`, each section prefixed by the file’s relative path.
- Cross-platform (Windows, macOS, Linux).
- Zero third-party dependencies.

---

## Features

- **Auto-excludes** common folders: `.git`, `.idea`, `.venv`, `venv`.
- **Folder excludes**: `--exclude node_modules,__pycache__,...` (matched by folder name at any depth).
- **Glob ignores**: `--ignore "*.min.js,*.map,dist/**"` (applies to both tree and bundle; affects files & dirs).
- **Custom extensions**: `--exts ".txt,.md,.py"` (case-insensitive, leading dots supported).
- **Include specific files**: `--include-names "Dockerfile,README"` (for files without extensions).
- **Custom outputs & root**: `--out`, `--bundle`, `--root`.

---

## Quick start

1) Copy the script into your repo root as `treeme.py`.

2) Run with defaults:

```bash
python treeme.py
````

Outputs:

  - `tree.txt` — directory tree
  - `all_texts.txt` — concatenated file contents

-----

## CLI usage

```bash
python treeme.py \
  --exclude node_modules,__pycache__ \
  --ignore "*.min.js,*.map,build/**" \
  --exts ".txt,.sh,.py,.sql" \
  --include-names "Dockerfile,LICENSE" \
  --out tree.txt \
  --bundle all_texts.txt \
  --root .
```

### Options

| Flag | Description | Default |
|---|---|---|
| `--root` | Root directory to scan | `.` |
| `--exclude` | Comma-separated **folder names** to skip (matched anywhere in the tree) | *(none, besides auto-excludes)* |
| `--ignore` | Comma-separated **glob patterns** to ignore (files **and** dirs). Examples: `*.min.js,*.map,dist/**,site/**` | *(none)* |
| `--exts` | Comma-separated file extensions to include in the bundle (leading dots OK; case-insensitive) | `.txt,.sh,.py,.sql` |
| `--include-names` | Comma-separated **exact filenames** to include (e.g., 'Dockerfile,README'). | *(none)* |
| `--out` | Output path for the tree file | `tree.txt` |
| `--bundle` | Output path for the concatenated file | `all_texts.txt` |

**Auto-excludes (always on):** `.git`, `.idea`, `.venv`, `venv`.

-----

## Examples

**Basic (defaults):**

```bash
python treeme.py
```

**Skip heavy/vendor folders and minified assets:**

```bash
python treeme.py \
  --exclude node_modules,__pycache__ \
  --ignore "*.min.js,*.map,dist/**"
```

**Collect Markdown too, and write to custom files:**

```bash
python treeme.py \
  --exts ".txt,.md,.py,.sql" \
  --out repo_tree.txt \
  --bundle repo_sources.txt
```

**Include specific files (like Dockerfile):**

```bash
python treeme.py \
  --exts ".py,.md,.sh" \
  --include-names "Dockerfile,LICENSE"
```

**Scan a subdirectory only:**

```bash
python treeme.py --root tools/
```

-----

## Sample output

**tree.txt (excerpt)**

```
my-project/
├── README.md
├── treeme.py
├── src/
│   ├── app.py
│   └── utils/
│       └── io.py
└── scripts/
    └── deploy.sh
```

**all\_texts.txt (excerpt)**

```
================================================================================
FILE: src/app.py
================================================================================
# contents of src/app.py...

================================================================================
FILE: scripts/deploy.sh
================================================================================
#!/usr/bin/env bash
# contents of scripts/deploy.sh...
```

-----

## How it works

  - Walks the filesystem with `pathlib`.
  - Skips symlinks.
  - Applies **folder excludes** (by name) and **glob ignores** (paths/files).
  - Writes a Unicode ASCII tree.
  - Collects files by **extension** (from `--exts`) or **exact filename** (from `--include-names`) and concatenates them; each section is headed by `FILE: relative/path.ext`.
  - Reads files as UTF-8 with `errors="replace"` to avoid crashes on odd encodings.

-----

## Installation

No packages required. You need **Python 3.8+**.

```bash
python --version
# Python 3.8 or higher recommended

# Run from your repo root:
python treeme.py -h
```

-----

## Tips & troubleshooting

  - **Not seeing a file in the bundle?** Ensure its extension is in `--exts`, or if it has no extension (like `Dockerfile`), add it with `--include-names "Dockerfile"`. Also check that it isn’t excluded/ignored.
  - **Too many files?** Add `--ignore` globs like `*.min.js,*.map,**/build/**,**/dist/**`.
  - **Large repos** Consider running from a narrower `--root` or add more ignores to speed up scanning.
  - **Windows paths** Globs use POSIX semantics internally for matching relative paths; typical patterns like `dist/**` work across platforms.
  - **Encoding issues** Non-UTF-8 bytes are replaced, not fatal. If you need strict mode, we can add a flag.

-----

## Security/Privacy

This tool **reads** files; it does not execute them. Review your `--ignore`, `--exts`, and `--include-names` to avoid bundling secrets or large artifacts. Consider adding patterns like `**/.env*`, `**/secrets/**`, `**/.DS_Store`, etc.

-----

## Contributing

Issues and PRs are welcome:

  - Feature requests (e.g., include/exclude by regex, output JSON tree, parallel walk).
  - Performance tweaks and tests.
  - Windows/macOS/Linux edge cases.

-----

## License

## MIT

## Changelog

  - **v1.2** — Added `--include-names` flag to bundle specific filenames (e.g., `Dockerfile`).
  - **v1.1** — CLI flags (`--exclude`, `--ignore`, `--exts`, `--root`, `--out`, `--bundle`), non-interactive flow.
  - **v1.0** — Initial version with interactive prompts.

-----

## Acknowledgements

Built to make sharing and auditing project structures painless. Enjoy\!
