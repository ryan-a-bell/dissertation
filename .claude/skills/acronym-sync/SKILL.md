---
name: acronym-sync
description: Synchronize acronym definitions with usage across dissertation chapters. Flags undefined acronyms, unused definitions, and inconsistent usage patterns.
allowed-tools: Read, Grep, Glob
---

# Acronym Sync

Check that acronym definitions and usage are consistent across the dissertation.

## File Locations

- **Definitions**: `manuscript/overleaf/acronyms.tex` and `manuscript/overleaf/acronym-list.tex`
- **Usage**: all `.tex` files under `manuscript/overleaf/` (chapters, appendices, front matter)

## Procedure

### Step 1: Parse definitions

Read `acronyms.tex` and `acronym-list.tex`. Extract all acronym definitions from commands like:
- `\newacronym{<key>}{<short>}{<long>}`
- `\newglossaryentry{<key>}{...}`
- `\DeclareAcronym{<key>}{...}`

Record for each: key, short form, long form.

### Step 2: Find all usage

Scan all `.tex` files (excluding the definition files) for acronym usage commands:
- `\ac{<key>}`, `\Ac{<key>}` -- standard use
- `\acp{<key>}`, `\Acp{<key>}` -- plural
- `\acs{<key>}`, `\acl{<key>}` -- short/long form
- `\acf{<key>}`, `\Acf{<key>}` -- full form
- `\gls{<key>}`, `\Gls{<key>}`, `\glspl{<key>}` -- glossary commands
- `\acrshort{<key>}`, `\acrlong{<key>}`, `\acrfull{<key>}` -- alternative forms

Record each key, the command used, and file:line.

### Step 3: Flag issues

1. **Undefined acronyms**: Keys used in `.tex` files but not defined in either definition file
2. **Unused definitions**: Keys defined but never used in any `.tex` file
3. **Hardcoded acronyms**: Instances where the short form text (e.g., "LLM") appears in running text without using `\ac{}` -- check for common acronyms only (top 10 most-used defined acronyms)
4. **Inconsistent first use**: Cases where `\acs{}` (short-only) is used in a chapter before any `\ac{}` or `\acf{}` call, meaning the reader may never see the expanded form in that chapter

### Step 4: Usage statistics

Count how many times each acronym is used and in which chapters.

## Output Format

```
## Acronym Sync Report

### Summary
- Defined acronyms: N
- Used acronyms: N
- Undefined (used but not defined): N
- Unused (defined but never used): N

### Undefined Acronyms
- `\ac{<key>}` in <file>:<line> -- not defined

### Unused Definitions
- <key> (<short> = <long>) -- defined in <file>:<line>, never used

### Hardcoded Usage (should use \ac{})
- <file>:<line> -- "<short>" appears as plain text, consider `\ac{<key>}`

### Usage by Chapter
| Acronym | Short | ch1 | ch2 | ch3 | ch4 | ch5 | ch6 | Total |
|---------|-------|-----|-----|-----|-----|-----|-----|-------|
| llm | LLM | 5 | 12 | 3 | 8 | 2 | 1 | 31 |
| ... | | | | | | | | |
```

Omit sections with zero results.
