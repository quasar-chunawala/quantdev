#!/usr/bin/env python3
"""
fetch_snippets.py

Downloads source files from GitHub (pinned to a commit SHA) into a local
`snippets/` folder so they can be embedded with the quarto-ext/include-code-files
extension, e.g.:

    ```{.python include="snippets/model.py" startLine=10 endLine=20}
    ```

Run manually with `python fetch_snippets.py`, or wire it up as a Quarto
pre-render script (see notes at the bottom of this file).
"""

from __future__ import annotations
import sys
import urllib.request
import urllib.error
from pathlib import Path

# --------------------------------------------------------------------------
# EDIT THIS LIST: one entry per file you want to pull in.
#
# - Pin `ref` to a commit SHA, not a branch name, so line numbers referenced
#   in your posts don't silently drift if the upstream file changes.
# - `dest` is the local path (relative to this script) the file is saved to.
# --------------------------------------------------------------------------
FILES = [
    {
        "owner": "abseil",
        "repo": "abseil-cpp",
        "ref": "2c004366e983c5be8334ac1ea3d4420e8fbcbea7",
        "path": "absl/container/internal/raw_hash_set.h",
        "dest": "../posts/flat-map-internals/raw_hash_set.h",
    },
    {
        "owner": "abseil",
        "repo": "abseil-cpp",
        "ref": "2c004366e983c5be8334ac1ea3d4420e8fbcbea7",
        "path": "absl/container/internal/raw_hash_map.h",
        "dest": "../posts/flat-map-internals/raw_hash_map.h",
    },
    {
        "owner": "abseil",
        "repo": "abseil-cpp",
        "ref": "2c004366e983c5be8334ac1ea3d4420e8fbcbea7",
        "path": "absl/container/internal/common.h",
        "dest": "../posts/flat-map-internals/common.h",
    },
    {
        "owner": "abseil",
        "repo": "abseil-cpp",
        "ref": "2c004366e983c5be8334ac1ea3d4420e8fbcbea7",
        "path": "absl/container/flat_hash_map.h",
        "dest": "../posts/flat-map-internals/flat_hash_map.h",
    },
    # Add more dicts here as needed.
]

RAW_URL_TEMPLATE = "https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"


def fetch_file(entry: dict, root: Path) -> None:
    url = RAW_URL_TEMPLATE.format(
        owner=entry["owner"], repo=entry["repo"], ref=entry["ref"], path=entry["path"]
    )
    dest = root / entry["dest"]
    dest.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {url}")
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            if response.status != 200:
                raise urllib.error.HTTPError(
                    url, response.status, "Non-200 status", None, None
                )
            content = response.read()
    except urllib.error.HTTPError as e:
        print(f"  ERROR: HTTP {e.code} fetching {url}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"  ERROR: could not reach {url} ({e.reason})", file=sys.stderr)
        sys.exit(1)

    dest.write_bytes(content)
    print(f"  Saved to {dest} ({len(content)} bytes)")


def main() -> None:
    root = Path(__file__).resolve().parent
    if not FILES or FILES[0]["owner"] == "OWNER":
        print(
            "No files configured yet — edit the FILES list at the top of "
            "fetch_snippets.py before running.",
            file=sys.stderr,
        )
        sys.exit(1)

    for entry in FILES:
        fetch_file(entry, root)

    print(f"Done: {len(FILES)} file(s) fetched.")


if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------
# Wiring this into Quarto as a pre-render step
# --------------------------------------------------------------------------
# In your project's _quarto.yml:
#
#   project:
#     pre-render: python fetch_snippets.py
#
# Or, for a single post, add it to that post's YAML front matter instead:
#
#   ---
#   title: "My Post"
#   filters:
#     - include-code-files
#   pre-render: python fetch_snippets.py
#   ---
#
# Then reference the downloaded files with line ranges in the post body:
#
#   ```{.python include="snippets/file.py" startLine=10 endLine=20}
#   ```
# --------------------------------------------------------------------------
