#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <num1> <num2>"
    exit 1
fi

# Assign input arguments to variables
a=$1
b=$2

# Find the minimum using arithmetic expansion
min=$(( a < b ? a : b ))

# Print the result
echo "$min"
