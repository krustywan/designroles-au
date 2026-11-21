#!/usr/bin/env bash
set -e
python discovery/debug2.py || true
python discovery/test_sources.py discovery/new_sources.json
