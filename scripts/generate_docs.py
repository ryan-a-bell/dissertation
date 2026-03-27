import os
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
INDEX_MD = DOCS_DIR / "index.md"
VIZ_INDEX = VIZ_DEST / "index.md"


def write_md(path, content):
    """Write markdown content to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        f.write(content)


def clean_dest():
    """Clean the destination directory."""
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)


def copy_source_tree():
    """Copy the contents of SRC_DIR to DEST respecting .gitignore."""
    clean_dest()
    
    # Load gitignore patterns
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with gitignore_path.open() as f:
            spec = PathSpec.from_lines('gitwildmatch', f)
    else:
        spec = PathSpec.from_lines('gitwildmatch', [])

    for src_path in SRC_DIR.rglob('*'):
        # Skip junk directories
        if any(part in ['__pycache__', '.ipynb_checkpoints', '.git'] for part in src_path.parts):
            continue
            
        rel_to_root = src_path.relative_to(Path('.'))
        check_path = rel_to_root.as_posix()
        if src_path.is_dir():
            check_path += '/'
        if spec.match_file(check_path):
            continue

        dest_path = DEST / src_path.relative_to(SRC_DIR)
        
        if src_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
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


def copy_viz_tree():
    """Copy the contents of VIZ_DIR to VIZ_DEST respecting .gitignore."""
    if not VIZ_DIR.exists():
        return

    if VIZ_DEST.exists():
        shutil.rmtree(VIZ_DEST)
    VIZ_DEST.mkdir(parents=True, exist_ok=True)

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
    copy_viz_tree()
    copy_readme_to_index()
    print(f"Mirrored source tree to {DEST}, viz to {VIZ_DEST}, and updated {INDEX_MD}")


if __name__ == '__main__':
    main()
