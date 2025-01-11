#!/usr/bin/env bash

errors=0

ruff check --fix --quiet src
ruff format --quiet src
ruff check --fix src || errors=$?
ruff format src || errors=$?

exit $errors
