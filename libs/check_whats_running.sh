#!/bin/bash/

# iterates over an ensemble and gives an update on the
# progress of each run. It will report on whether they are:
#   a) completed
#   b) still running and, if so, how many years they have done so far
#   c) not completed but are also not running (possibly crashed)

# inputs:
#   - ensemble_dir: path to ensemble home directory

usage() { echo "Usage: $0 <ensemble_dir>" 1>&2; exit 1; }

if [ "$#" -ne 1 ]; then
    usage
fi 

running_jobs=$(squeue --noheader --format=%j --me)

ENSEMBLE=$1
PYTHON_ENV=$WORK/postprocessing # python envrionment using venv
MAX_TIME=9990 # time at which a job should be considered complete

# activate python environment
source $PYTHON_ENV/bin/activate

# iterate over ensemble members
for run in "$ENSEMBLE/run*"; do

    last_plotfile=$(ls "$run/plot" | tail -n 1)
    years_complete=$(python $WORK/libs/get_timestep.py $run/plot/$last_plotfile)

    if [ $years_complete -ge $MAX_TIME ]; then
        echo "$run complete!"

    elif grep -q "$run" <<< "$running_jobs"; then
        echo "$run running... $years_complete years done so far"

    else
        echo "$run has not completed but is also not running"
    fi
done

# deactivate python environment
deactivate