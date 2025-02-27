#!/bin/bash

# Function to find the minimum of two numbers
min() {

    local a=$1
    local b=$2

    local min=$(( a < b ? a : b ))

    echo "$min"
}

# Function to calculate elapsed time
time_elapsed() {

    local start_time=$1
    local end_time=$2

    local duration=$((end_time - start_time))
    local hours=$((duration / 3600))
    local minutes=$(((duration % 3600) / 60))

    echo "${hours}h ${minutes}m"
}

# Function to get the most recent file from a directory
get_latest_file() {

    local dir=${1%/}
	local pattern=$2
    local latest_file=$(ls -t "$dir"/$pattern 2>/dev/null | head -n 1)
    
    echo $(basename "$latest_file")
}
