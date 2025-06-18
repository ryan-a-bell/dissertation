import os
import shutil
import yaml
from pathlib import Path

"""
Automates the generation of project documentation by scanning and copying relevant files to the `docs` directory, and dynamically creating the 
`mkdocs.yml` configuration file with a customized navigation structure and theme settings 
tailored for the dissertation project.
"""

# Extensions we want to include
INCLUDE_EXTENSIONS = {'.md', '.ipynb', '.pdf', '.csv'}

# Files to exclude from documentation
EXCLUDE_FILES = {
    'README.md',  # Will be handled separately as index
    '.gitkeep',
    'placeholder.md'
}

# Directories to exclude
EXCLUDE_DIRS = {
    'docs',
    '.git',
    '__pycache__',
    '.pytest_cache',
    'site',
    '.venv',
    'venv'
}

def should_include(file_path):
    """Check if a file should be included in documentation."""
    path = Path(file_path)
    
    # Check extension
    if path.suffix not in INCLUDE_EXTENSIONS:
        return False
    
    # Check if file is in excluded list
    if path.name in EXCLUDE_FILES:
        return False
    
    # Check if any parent directory is excluded
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return False
    
    return True

def find_files():
    """Find all files to include in documentation."""
    source_files = []
    
    # Add README.md as index.md
    if os.path.exists('README.md'):
        source_files.append(('README.md', 'docs/index.md'))
    
    # Walk through all directories
    for root, dirs, files in os.walk("."):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for f in files:
            rel_path = os.path.join(root, f).replace("\\", "/").lstrip("./")
            if should_include(rel_path):
                dest_path = f"docs/{rel_path}"
                source_files.append((rel_path, dest_path))
    
    return source_files

def copy_files(file_map):
    """Copy files to docs directory."""
    for src, dest in file_map:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        print(f"Copied {src} -> {dest}")

def create_nav_entries(file_map):
    """Create navigation structure for MkDocs."""
    nav = []
    
    # Start with Home (index.md from README.md)
    nav.append({"Home": "index.md"})
    
    # Group files by directory structure
    grouped = {}
    
    for src, dest in file_map:
        if src == 'README.md':  # Skip README as it's already handled as Home
            continue
            
        rel_path = dest.replace("docs/", "")
        parts = rel_path.split("/")
        
        # Create a clean title from filename
        filename = parts[-1]
        title = filename.rsplit(".", 1)[0]
        
        # Clean up title formatting
        title = title.replace("_", " ").replace("-", " ")
        # Capitalize each word but preserve numbers and dots
        title = " ".join(word.capitalize() if not any(c.isdigit() for c in word) else word 
                        for word in title.split())
        
        if len(parts) == 1:
            # Top-level file
            nav.append({title: rel_path})
        else:
            # Nested file - group by directory
            section_path = "/".join(parts[:-1])
            section_name = create_section_name(section_path)
            
            if section_name not in grouped:
                grouped[section_name] = []
            
            grouped[section_name].append({title: rel_path})
    
    # Add grouped sections to nav in logical order
    section_order = ["Rubrics", "Figs", "Phase1 Prep", "Phase2 Conversion", 
                    "Phase3 Variants", "Phase4 Inference", "Phase5 Metrics", 
                    "Phase6 Tables", "Phase7 Analysis", "Src"]
    
    # Add sections in preferred order
    for section in section_order:
        if section in grouped:
            # Sort items within each section
            sorted_items = sorted(grouped[section], key=lambda x: list(x.keys())[0])
            nav.append({section: sorted_items})
            del grouped[section]
    
    # Add any remaining sections
    for section, items in sorted(grouped.items()):
        sorted_items = sorted(items, key=lambda x: list(x.keys())[0])
        nav.append({section: sorted_items})
    
    return nav

def create_section_name(section_path):
    """Create a clean section name from directory path."""
    parts = section_path.split("/")
    
    # Handle specific directory patterns
    if "phase" in parts[-1].lower():
        # Convert phase1_prep to "Phase1 Prep"
        part = parts[-1]
        if "_" in part:
            phase_part, desc_part = part.split("_", 1)
            return f"{phase_part.capitalize()} {desc_part.capitalize()}"
        else:
            return part.capitalize()
    
    # Default: capitalize and clean up
    return parts[-1].replace("_", " ").replace("-", " ").title()

def write_mkdocs_yml(nav, output='mkdocs.yml'):
    """Write the MkDocs configuration file."""
    config = {
        'site_name': 'Dissertation Documentation',
        'site_description': 'Documentation for dissertation project phases and analysis',
        'theme': {
            'name': 'material',
            'features': [
                'navigation.tabs',
                'navigation.sections',
                'navigation.expand',
                'navigation.top',
                'search.highlight',
                'search.share'
            ],
            'palette': {
                'scheme': 'default',
                'primary': 'blue',
                'accent': 'blue'
            }
        },
        'plugins': [
            'search',
            'mkdocs-jupyter'
        ],
        'markdown_extensions': [
            'admonition',
            'codehilite',
            'toc'
        ],
        'nav': nav
    }

    with open(output, 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False)
        print(f"Updated {output}")

if __name__ == "__main__":
    print("Generating MkDocs documentation...")
    file_map = find_files()
    print(f"Found {len(file_map)} files to include")
    
    copy_files(file_map)
    nav = create_nav_entries(file_map)
    write_mkdocs_yml(nav)
    
    print("Documentation generation complete!")
    print("Run 'mkdocs serve' to preview the documentation locally")
