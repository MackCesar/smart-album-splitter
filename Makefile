

# Smart Album Splitter — Makefile (WIP)
# Usage examples:
#   make setup
#   make run PROJECT=projects/tastes-like-velvet/project.yml
#   make detect PROJECT=projects/tastes-like-velvet/project.yml EMIT=json
#   make split PROJECT=projects/tastes-like-velvet/project.yml
#   make tag   PROJECT=projects/tastes-like-velvet/project.yml
#   make normalize PROJECT=projects/tastes-like-velvet/project.yml MODE=ebur128

PY ?= python
PROJECT ?= projects/demo-album/example.yml
EMIT ?= json          # json|csv|cue
MODE ?= ebur128       # ebur128 only (WIP)

.PHONY: help setup run detect split tag normalize clean

help:
	@echo "Targets (WIP):"
	@echo "  setup       - create venv and install requirements"
	@echo "  run         - download → detect → split → tag (uses $(PROJECT))"
	@echo "  detect      - detect timestamps and print/export (EMIT=$(EMIT))"
	@echo "  split       - split audio using existing tracklist.json"
	@echo "  tag         - (re)apply tags/cover to existing files"
	@echo "  normalize   - loudness normalize produced files (MODE=$(MODE))"
	@echo "  clean       - remove build caches (does not delete outputs)"

setup:
	$(PY) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	$(PY) -m smart_splitter.cli run $(PROJECT)

# Print to stdout by default; redirect with: make detect OUT=tracklist.json
# Example: make detect PROJECT=projects/tastes-like-velvet/project.yml EMIT=csv
ifdef OUT
	sed := \# placeholder to avoid make error
endif

detect:
	$(PY) -m smart_splitter.cli detect $(PROJECT) --emit $(EMIT) $(if $(OUT),--out $(OUT),)

split:
	$(PY) -m smart_splitter.cli split $(PROJECT)

tag:
	$(PY) -m smart_splitter.cli tag $(PROJECT)

normalize:
	$(PY) -m smart_splitter.cli normalize $(PROJECT) --mode $(MODE)

clean:
	rm -rf .venv .pytest_cache __pycache__