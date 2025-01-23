#!/bin/bash

# Turning BISICLES plotfiles into netcdfs is a lengthy process and is best done via a slurm job. 
# I prefer to generate one netcdf for each variable so that I can be more flexible with storage.
# This script generates job scripts for each variable based off of a template and then queues them.

# inputs:
#   - ensemble_dir: path to ensemble home directory
#   - job_template: path to a template job script with '@VAR' in place of variable names

usage() { echo "Usage: $0 <ensemble_dir> <job_template>" 1>&2; exit 1; }

if [ "$#" -ne 2 ]; then
    usage
fi

ENSEMBLE=$1
TEMPLATE=$2
outdir=$ENSEMBLE/postprocessing
mkdir -p $outdir

for var in 'calvingFlux' 'calvingRate' 'dragCoef' 'iceFrac' 'sTemp' 'viscosityCoef' 'waterDepth'; do
    sed -e s/@VAR/$var/ $TEMPLATE > "$outdir/process_${var}.sh"
    cd $outdir
    sbatch process_${var}.sh
done
