#!/usr/bin/env bash

set -v

errors=0

if ! git diff --quiet pyproject.toml; then
    uv pip install -e '.' || errors=$?
fi

uv run wzrd --help || errors=$?
uv run wzrd --show-config || errors=$?
uv run wzrd print the first ten primes || errors=$?

exit $errors
