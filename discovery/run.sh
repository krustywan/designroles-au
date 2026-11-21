#!/usr/bin/env bash
# What the testing-only Probe workflow runs on probe/* branches.
set -e
python discovery/test_sources.py discovery/new_sources.json
