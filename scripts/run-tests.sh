#!/bin/bash

# making out dir
mkdir -p /pqc/output

# Moving to the build directory
cd /pqc/pqc-docker/bin

pwd

# Running sig mem test
python3 run_mem.py test_sig_mem