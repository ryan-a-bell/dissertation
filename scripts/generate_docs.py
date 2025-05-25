import os
import shutil
import yaml

# Extensions we want to include
INCLUDE_EXTENSIONS = {'.md', '.ipynb', '.csv'}  # MkDocs can't render CSV but you can link to them

# Ignore files already in docs/ to avoid recursion or overwriting real docs
def should_include(file_path):
    ext = os.path.splitext(file_path)[-1]
    return ext in INCLUDE_EXTENSIONS and not file_path.startswith("docs/")

def find_files():
    source_files = []
    for root, _, files in os.walk("."):
        for f in files:
            rel_path = os.path.join(root, f).replace("\\", "/").lstrip("./")
            if should_include(rel_path):
                dest_path = f"docs/{rel_path}"
                source_files.append((rel_path, dest_path))
    return source_files

def copy_files(file_map):
    for src, dest in file_map:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        print(f"Copied {src} -> {dest}")

def create_nav_entries(file_map):
    nav = []
    grouped = {}

    for _, dest in file_map:
        rel = dest.replace("docs/", "")
        parts = rel.split("/")
        title = parts[-1].rsplit(".", 1)[0].replace("_", " ").title()

        # Deep nest: group by top-level folder
        if len(parts) > 1:
            section = parts[0].title()
            if section not in grouped:
                grouped[section] = []
            grouped[section].append({title: rel})
        else:
            nav.append({title: rel})

    # Merge grouped sections into nav
    for section, items in grouped.items():
        nav.append({section: sorted(items, key=lambda x: list(x.keys())[0])})
    return nav

def write_mkdocs_yml(nav, output='mkdocs.yml'):
    config = {
        'site_name': 'My Project Docs',
        'theme': {'name': 'material'},
        'plugins': ['search', 'mkdocs-jupyter'],
        'nav': nav
    }

    with open(output, 'w') as f:
        yaml.dump(config, f, sort_keys=False)
        print(f"Updated {output}")

if __name__ == "__main__":
    file_map = find_files()
    copy_files(file_map)
    nav = create_nav_entries(file_map)
    write_mkdocs_yml(nav)
