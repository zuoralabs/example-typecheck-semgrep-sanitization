#!/usr/bin/env bash

./run-mypy.bash
./run-semgrep.bash
python sanitization_check_example.py
