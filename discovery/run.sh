#!/usr/bin/env bash
pip -q install pillow cairosvg
python3 discovery/logo_probe.py 2>&1 | grep -E "CAND|ERR" | cut -c1-200
