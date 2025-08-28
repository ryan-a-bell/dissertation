import os
import shutil
from pathlib import Path
import pandas as pd
from pathspec import PathSpec

SRC_DIR = Path('src')
DOCS_DIR = Path('docs')
DEST = Path("docs", "source-code", "src")


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


def main():
    copy_source_tree()
    print(f'Mirrored source tree to {DEST}')


if __name__ == '__main__':
    main()
