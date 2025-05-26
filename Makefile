# Makefile for setup and running tasks

.PHONY: docs docs-serve docs-build clean-docs

# Generate documentation
docs: clean-docs
	python scripts/generate_docs.py
	mkdocs build

# Serve documentation locally
docs-serve: clean-docs
	python scripts/generate_docs.py
	mkdocs serve

# Build documentation only
docs-build:
	mkdocs build

# Clean generated documentation files
clean-docs:
	rm -rf docs/src docs/rubrics docs/figs 2>/dev/null || true
	rm -rf site 2>/dev/null || true
