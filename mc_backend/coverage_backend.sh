#!/bin/bash
source ../venv/bin/activate
coverage run --rcfile=.coveragerc tests.py
coverage combine && coverage report -m
