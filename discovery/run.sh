#!/usr/bin/env bash
# What the probe workflow runs. Edit on a probe/* branch to test something from GitHub's computers.
set -e
python discovery/probe.py discovery/companies.csv
