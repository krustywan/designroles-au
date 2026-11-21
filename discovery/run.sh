#!/usr/bin/env bash
set -e
SECONDS=0
python run.py
python build_board.py
echo "ELAPSED $SECONDS s"
mkdir -p discovery/out && cp jobs.json discovery/out/
python -c "import json;[print(\"ROLE\", j[\"source\"], \"|\", j[\"employer\"], \"|\", j[\"title\"], \"|\", j[\"discipline\"], \"|\", j[\"link_type\"]) for j in json.load(open(\"jobs.json\"))[\"jobs\"]]"
