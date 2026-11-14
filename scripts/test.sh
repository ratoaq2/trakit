#!/bin/bash

set -ex

uv run ruff check trakit tests
uv run ruff format --check trakit tests
uv run mypy trakit tests
uv run pytest -q --tb=short tests
uv run python scripts/check_knowledge.py
