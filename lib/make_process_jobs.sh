#!/bin/bash

# Turning BISICLES plotfiles into netcdfs is a lengthy process and is best done via a slurm job. 
# I prefer to generate one netcdf for each variable so that I can be more flexible with storage.
# This script generates job scripts for each variable based off of a template and then queues them.

# inputs:
#   - ensemble_dir: path to ensemble home directory
#   - job_template: path to a template job script with '@VAR' in place of variable names

usage() { echo "Usage: $0 <job_array_template> <ensemble_directory> <num_runs> <lev>" 1>&2; exit 1; }

if [ "$#" -ne 4 ]; then
    usage
fi

TEMPLATE=$1
ENSEMBLE=$2
NUM_RUNS=$3
LEV=$4
OUTDIR=$ENSEMBLE/postprocessing
mkdir -p $OUTDIR

for VAR in 'thickness' 'Z_base' 'Z_surface' 'xVel' 'yVel' 'dThickness/dt'; do
    sed -e "s/@VAR/$VAR/g" -e "s/@LEV/$LEV/g" -e "s/@NUM_RUNS/$NUM_RUNS/g" $TEMPLATE > "$OUTDIR/job_array.process_${VAR}.sh"
done
