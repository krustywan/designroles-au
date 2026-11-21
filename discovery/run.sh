#!/usr/bin/env bash
set -e
python run.py > discovery/out_run.txt 2>&1 || (tail -40 discovery/out_run.txt; exit 1)
grep -i "first-seen\|kept:" discovery/out_run.txt
echo "B64START"; gzip -9c jobs.json | base64 -w0; echo; echo "B64END"
