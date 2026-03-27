# CLAUDE.md

## Refreshing the Dissertation Timeline

The timeline on the docs landing page (`docs/index.md`) is a pre-rendered SVG from a PlantUML source file.

**Source:** `docs/assets/timeline.puml`
**Rendered:** `docs/assets/timeline.svg`

To update the timeline:

1. Edit `docs/assets/timeline.puml` with the desired changes.
2. Re-render the SVG:
   ```bash
   java -jar plantuml.jar -tsvg -o docs/assets/ docs/assets/timeline.puml
   ```
3. Commit both `timeline.puml` and `timeline.svg`.

## Project Preferences

- Do not use emojis in code, documentation, commit messages, or any file output unless the user explicitly requests it.
