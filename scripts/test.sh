#!/bin/bash

set -ex

uv run ruff check trakit tests
uv run ruff format --check trakit tests
uv run mypy trakit
uv run pytest trakit -vv tests
