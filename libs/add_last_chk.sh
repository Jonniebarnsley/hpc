#!/bin/bash

usage() { echo "Usage: $0 <input_file> <checkpoint_directory>" 1>&2; exit 1; }

# Ensure the correct number of inputs
if [[ $# -ne 2 ]]; then
    usage
fi

BISINPT=$1
CHKDIR=$2

# Ensure the input file exists and is readable
if [[ ! -f "$BISINPT" || ! -r "$BISINPT" ]]; then
    echo "Error: '$BISINPT' does not exist or is not readable" >&2
    exit 1
fi

# Ensure the checkpoint dir is a valid directory
if [[ ! -d "$CHKDIR" ]]; then
    echo "Error: directory '$CHKDIR' does not exist" >&2
    exit 1
fi

# Check for the most recently created checkpoint file
lastchk=$(ls -t $CHKDIR/chk.*.2d.hdf5 2>/dev/null | head -n 1)

# If no checkpoint file is found, start do nothing
if [ -n "$lastchk" ]; then
    echo "amr.restart_file = $lastchk" >> "$BISINPT"
    echo "amr.restart_set_time=false" >> "$BISINPT"
fi