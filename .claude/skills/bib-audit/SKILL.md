---
name: bib-audit
description: Audit bibliography files for integrity issues. Finds duplicate keys, missing required fields, unused citations, and uncited references across the dissertation LaTeX source.
allowed-tools: Read, Grep, Glob, Bash(grep *), Bash(sort *), Bash(wc *)
---

# Bibliography Audit

Scan all `.bib` files and `.tex` files in the dissertation manuscript and report integrity issues.

## Bibliography Locations

- `manuscript/overleaf/references.bib` -- primary bibliography
- `manuscript/overleaf/references-example.bib` -- example/template (skip during audit)
- `manuscript/sources/*.bib` -- topic-organized bibliography files

## TeX Source Locations

- `manuscript/overleaf/*.tex` -- all chapter, appendix, and front matter files

## Audit Procedure

### Step 1: Parse all .bib files

For each `.bib` file (excluding `references-example.bib` and files under `Templates/` or `Examples/`):
- Extract all entry keys (the identifier after `@type{`)
- Extract entry types (`@article`, `@inproceedings`, `@misc`, etc.)
- For each entry, check which fields are present

### Step 2: Check for duplicate keys

Report any citation key that appears in more than one `.bib` file, or more than once in the same file. Include the file paths and line numbers for each occurrence.

### Step 3: Validate required fields

Check each entry has the required fields for its type:

| Type | Required Fields |
|------|----------------|
| `@article` | author, title, journal, year |
| `@inproceedings` | author, title, booktitle, year |
| `@book` | author/editor, title, publisher, year |
| `@phdthesis` / `@mastersthesis` | author, title, school, year |
| `@techreport` | author, title, institution, year |
| `@misc` | author, title, year (or note) |
| `@online` | author/title, url, year |

Report entries with missing required fields.

### Step 4: Find uncited references

Collect all `\cite{...}`, `\citep{...}`, `\citet{...}`, `\citeauthor{...}`, and `\citeyear{...}` keys from all `.tex` files. Multi-key citations like `\cite{key1,key2}` should be split.

Report any bib entry key that is never cited in any `.tex` file.

### Step 5: Find orphaned citations

Report any citation key used in a `.tex` file that does not exist in any `.bib` file.

### Step 6: Additional checks

- Flag entries where `year` is missing or not a valid 4-digit number
- Flag entries with empty `title` or `author` fields
- Flag potential duplicate entries (different keys but identical title+year)

## Output Format

```
## Bibliography Audit Report

### Summary
- Total .bib files scanned: N
- Total entries: N
- Total unique citation keys used in .tex: N

### Duplicate Keys
- <key>: found in <file1>:<line>, <file2>:<line>

### Missing Required Fields
- <file>: <key> (@type) -- missing: <field1>, <field2>

### Orphaned Citations (cited but not defined)
- <key> -- cited in <file>:<line>

### Uncited References (defined but never cited)
- <file>: <key> (@type)

### Potential Duplicates (same title+year, different keys)
- <key1> / <key2>: "<title>" (<year>)

### Statistics
- Entries with issues: N
- Clean entries: N
```

Omit any section with zero results.
