import os
import re
import shutil
from pathlib import Path
import pandas as pd
from pathspec import PathSpec

SRC_DIR = Path("src")
VIZ_DIR = Path("viz")
DOCS_DIR = Path("docs")
DEST = Path("docs", "source-code")
VIZ_DEST = Path("docs", "visualizations")
README = Path("README.md")
DOCSIGNORE = SRC_DIR / ".docsignore"
INDEX_MD = DOCS_DIR / "index.md"
VIZ_INDEX = VIZ_DEST / "index.md"


def write_md(path, content):
    """Write markdown content to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        f.write(content)


PRESERVE_PATTERNS = {"index.md", ".pages.yml", "modality-evaluation-pipeline.jpg"}


def load_docsignore():
    """Load exclusion patterns from src/.docsignore.

    Returns a list of path prefixes (relative to SRC_DIR) that should be
    skipped during source-tree copying.
    """
    if not DOCSIGNORE.exists():
        return []
    patterns = []
    for line in DOCSIGNORE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def clean_dest():
    """Clean generated files from DEST while preserving manually-maintained files.

    Files matching PRESERVE_PATTERNS (index.md, .pages.yml, and the pipeline
    diagram) are kept in place so that the source-code section retains its
    hand-written overview pages and navigation after regeneration.
    """
    if not DEST.exists():
        DEST.mkdir(parents=True, exist_ok=True)
        return

    # Collect preserved files into a temp dict keyed by relative path
    preserved = {}
    for path in DEST.rglob("*"):
        if path.is_file() and path.name in PRESERVE_PATTERNS:
            rel = path.relative_to(DEST)
            preserved[rel] = path.read_bytes()

    shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)

    # Restore preserved files
    for rel, data in preserved.items():
        restored = DEST / rel
        restored.parent.mkdir(parents=True, exist_ok=True)
        restored.write_bytes(data)


def copy_source_tree():
    """Copy the contents of SRC_DIR to DEST respecting .gitignore and .docsignore."""
    clean_dest()

    # Load gitignore patterns
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with gitignore_path.open() as f:
            spec = PathSpec.from_lines('gitwildmatch', f)
    else:
        spec = PathSpec.from_lines('gitwildmatch', [])

    # Load docsignore patterns
    docsignore_patterns = load_docsignore()

    for src_path in SRC_DIR.rglob('*'):
        # Skip junk directories
        if any(part in ['__pycache__', '.ipynb_checkpoints', '.git'] for part in src_path.parts):
            continue

        # Skip .docsignore itself
        if src_path.name == '.docsignore':
            continue

        rel_to_root = src_path.relative_to(Path('.'))
        check_path = rel_to_root.as_posix()
        if src_path.is_dir():
            check_path += '/'
        if spec.match_file(check_path):
            continue

        # Check docsignore patterns (paths relative to SRC_DIR)
        rel_to_src = src_path.relative_to(SRC_DIR).as_posix()
        if src_path.is_dir():
            rel_to_src += '/'
        if any(rel_to_src.startswith(pat) for pat in docsignore_patterns):
            continue

        dest_path = DEST / src_path.relative_to(SRC_DIR)

        if src_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        # Skip README.md when a hand-maintained index.md already exists
        if src_path.name == 'README.md' and (dest_path.parent / 'index.md').exists():
            continue

        # Handle different file types
        if src_path.suffix == '.csv':
            # Create CSV stub with relative link
            write_md(dest_path.with_suffix(".md"),
                    f"# Preview of `{src_path.name}`\n\n{{{{ read_csv('./{src_path.name}') }}}}\n")
            # Copy the actual CSV file
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
        elif src_path.suffix == '.pdf':
            # Create PDF stub with relative link
            write_md(dest_path.with_suffix(".md"),
                    f"[Download **{src_path.name}**](./{src_path.name})\n")
            # Copy the actual PDF file
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
        else:
            # Copy other files directly
            dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)


def clean_viz_dest():
    """Clean generated files from VIZ_DEST while preserving manually-maintained files."""
    if not VIZ_DEST.exists():
        VIZ_DEST.mkdir(parents=True, exist_ok=True)
        return

    preserved = {}
    for path in VIZ_DEST.rglob("*"):
        if path.is_file() and path.name in PRESERVE_PATTERNS:
            rel = path.relative_to(VIZ_DEST)
            preserved[rel] = path.read_bytes()

    shutil.rmtree(VIZ_DEST)
    VIZ_DEST.mkdir(parents=True, exist_ok=True)

    for rel, data in preserved.items():
        restored = VIZ_DEST / rel
        restored.parent.mkdir(parents=True, exist_ok=True)
        restored.write_bytes(data)


def copy_viz_tree():
    """Copy the contents of VIZ_DIR to VIZ_DEST respecting .gitignore."""
    if not VIZ_DIR.exists():
        return

    clean_viz_dest()

    # Load gitignore patterns
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with gitignore_path.open() as f:
            spec = PathSpec.from_lines('gitwildmatch', f)
    else:
        spec = PathSpec.from_lines('gitwildmatch', [])

    for viz_path in VIZ_DIR.rglob('*'):
        if any(part in ['__pycache__', '.ipynb_checkpoints', '.git'] for part in viz_path.parts):
            continue

        rel_to_root = viz_path.relative_to(Path('.'))
        check_path = rel_to_root.as_posix()
        if viz_path.is_dir():
            check_path += '/'
        if spec.match_file(check_path):
            continue

        dest_path = VIZ_DEST / viz_path.relative_to(VIZ_DIR)

        if viz_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        if viz_path.suffix == '.csv':
            write_md(dest_path.with_suffix(".md"),
                    f"# Preview of `{viz_path.name}`\n\n{{{{ read_csv('./{viz_path.name}') }}}}\n")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(viz_path, dest_path)
        elif viz_path.suffix == '.pdf':
            write_md(dest_path.with_suffix(".md"),
                    f"[Download **{viz_path.name}**](./{viz_path.name})\n")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(viz_path, dest_path)
        elif viz_path.suffix == '.mp4':
            # Create a markdown page that embeds the video
            write_md(dest_path.with_suffix(".md"),
                    f"# {viz_path.stem.replace('_', ' ').title()}\n\n"
                    f"<video controls width=\"100%\">\n"
                    f"  <source src=\"./{viz_path.name}\" type=\"video/mp4\">\n"
                    f"  Your browser does not support the video tag.\n"
                    f"</video>\n\n"
                    f"[Download **{viz_path.name}**](./{viz_path.name})\n")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(viz_path, dest_path)
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(viz_path, dest_path)

    # Write a landing page for the visualizations section
    video_path = VIZ_DEST / "viz-outputs" / "repo_lineage.mp4"
    video_embed = ""
    if video_path.exists():
        video_embed = (
            "## Repository Lineage Video\n\n"
            "This animated visualization shows the evolution of the repository over time, "
            "generated using [Gource](https://gource.io/).\n\n"
            "<video controls width=\"100%\">\n"
            "  <source src=\"./viz-outputs/repo_lineage.mp4\" type=\"video/mp4\">\n"
            "  Your browser does not support the video tag.\n"
            "</video>\n\n"
        )

    write_md(VIZ_INDEX,
        "# Visualizations\n\n"
        "Visual artifacts and tools for exploring the dissertation repository.\n\n"
        f"{video_embed}"
        "## Contents\n\n"
        "- **viz-outputs/** — Generated visualizations (videos, images)\n"
        "- **repository_lineage_storytelling.ipynb** — Notebook for git repository analysis\n"
        "- **repository_lineage_storytelling_with_gource.md** — Guide for creating Gource animations\n"
    )


def copy_viz_assets():
    """Copy key visualization assets to docs/assets/ for use on the home page."""
    video_src = VIZ_DIR / "viz-outputs" / "repo_lineage.mp4"
    if video_src.exists():
        video_dest = DOCS_DIR / "assets" / "repo_lineage.mp4"
        video_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(video_src, video_dest)


def copy_readme_to_index():
    """Copy README.md to docs/index.md and adjust relative links.

    Skipped if docs/index.md already exists and has been customized
    (i.e., does not start with the README's first line).
    """
    if not README.exists():
        return

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Preserve a manually-curated index.md
    if INDEX_MD.exists():
        existing = INDEX_MD.read_text(encoding="utf-8")
        readme_first_line = README.read_text(encoding="utf-8").split("\n", 1)[0]
        if not existing.startswith(readme_first_line):
            return

    content = README.read_text(encoding="utf-8")
    content = content.replace("](LICENSE)", "](../LICENSE)")
    write_md(INDEX_MD, content)


def main():
    copy_source_tree()
    copy_viz_assets()
    copy_readme_to_index()
    print(f"Mirrored source tree to {DEST} and updated {INDEX_MD}")


if __name__ == '__main__':
    main()
