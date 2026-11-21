#!/usr/bin/env bash
set -e
python run.py > discovery/out_run.txt 2>&1 || (tail -40 discovery/out_run.txt; exit 1)
tail -5 discovery/out_run.txt
python discovery/check.py
