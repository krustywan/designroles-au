#!/usr/bin/env bash
set -e
python fetch_logos.py
echo "B64START"; tar czf - logos | base64 -w0; echo; echo "B64END"
