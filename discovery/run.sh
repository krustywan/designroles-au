#!/usr/bin/env bash
set -e
pip -q install pillow cairosvg
python discovery/logo_probe.py
