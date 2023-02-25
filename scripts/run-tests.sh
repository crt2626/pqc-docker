#!/bin/bash

# Moving script 
# cd /pqc/pqc-docker/scripts
# cp run_mem.py /pqc/pqc-docker/bin

# making out dir
mkdir -p /pqc/pqc-docker/output

# Moving to the build directory
cd /pqc/pqc-docker/bin/

# Running sig mem test
python3 run_mem.py /pqc/pqc-docker/bin/test_sig_mem