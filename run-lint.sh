#!/usr/bin/env bash

errors=0

command -v ruff >/dev/null || with_ruff="--with ruff"
uvx --from 'git+https://github.com/akaihola/darker@fix-packaging' --with isort ${with_ruff} darker . || errors=$?
uvx --with mypy --with pydocstyle --with '.' ${with_ruff} graylint . || errors=$?

exit $errors
