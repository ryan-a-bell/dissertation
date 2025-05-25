import os
import yaml

def scan_docs(folder):
    nav = []
    for root, dirs, files in os.walk(folder):
        # Skip hidden folders like .git or __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        rel_root = os.path.relpath(root, folder)
        section = []
        for f in sorted(files):
            if f.endswith(('.md', '.ipynb')):
                # Skip this script and mkdocs.yml
                if f in ('generate_mkdocs_yml.py', 'mkdocs.yml'):
                    continue

                # Build display title
                title = f.replace(".md", "").replace(".ipynb", "").replace("_", " ").title()
                # Path relative to root of docs
                doc_path = os.path.join(rel_root, f).replace("\\", "/")
                section.append({title: doc_path if rel_root == '.' else f"{rel_root}/{f}"})
        
        if section:
            section_title = rel_root.title() if rel_root != '.' else 'Home'
            nav.append({section_title: section} if section_title != 'Home' else section[0])
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

if __name__ == "__main__":
    # Use the directory where this script resides as the base
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nav = scan_docs(script_dir)
    write_mkdocs_yml(nav)
