#!/bin/bash

usage() { echo "Usage: $0 <input_file> <increment>" 1>&2; exit 1; }

# Ensure the correct number of inputs
if [[ $# -ne 2 ]]; then
    usage
fi

BISINPT="$1"
INCREMENT="$2"

# Ensure the file exists and is readable
if [[ ! -f "$BISINPT" || ! -r "$BISINPT" ]]; then
    echo "Error: '$BISINPT' does not exist or is not readable" >&2
    exit 1
fi

# Ensure increment is a valid number
if ! [[ "$INCREMENT" =~ ^[0-9]+$ ]]; then
    echo "Error: Increment must be a positive integer" >&2
    exit 1
fi

# Extract maxTime value
maxTime=$(grep '^main.maxTime' "$BISINPT" | tail -n 1 | awk -F '=' '{print $2}' | awk '{print $1}' | xargs)

# Ensure maxTime exists
if [[ -z "$maxTime" ]]; then
    echo "Error: cannot find maxTime in $BISINPT" >&2
    exit 1
fi

# increase maxTime by increment
newTime=$(( maxTime + INCREMENT ))
echo "main.maxTime = $newTime" >> $BISINPT

# Output maxTime
echo "$maxTime"