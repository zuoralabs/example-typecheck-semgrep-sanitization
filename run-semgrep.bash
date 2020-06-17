#!/usr/bin/env bash

# https://pypi.org/project/semgrep/

semgrep --config semgrep-config.yml sanitization_check_example.py --dangerously-allow-arbitrary-code-execution-from-rules
