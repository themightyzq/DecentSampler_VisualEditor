#!/bin/bash
cd "$(dirname "$0")"

# Install dependencies if needed
pip3 install -q -r requirements.txt
pip3 install -q -r requirements-optional.txt 2>/dev/null

# Launch
cd src
python3 main.py
