#!/bin/bash

usage() { echo "Usage: $0 <job_id_start> <job_id_end>" 1>&2; exit 1; }

if [ "$#" -ne 2 ]; then
    usage
fi

START=$1
END=$2

for jobid in {$START..$END}; do
    qdel $jobid
done