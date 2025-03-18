#!/usr/bin/env bash

set -v

errors=0

if ! git diff --quiet pyproject.toml; then
    uv pip install -e '.' || errors=$?
fi

uv run dare --help || errors=$?
uv run dare --show-config || errors=$?
uv run dare \
  --model openrouter/google/gemini-2.0-flash-exp:free \
  print the first ten primes \
  || errors=$?

exit $errors
