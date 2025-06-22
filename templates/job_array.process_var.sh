#!/bin/bash
# Slurm job options (job-name, compute nodes, job time)
#SBATCH --job-name=process_@VAR_@LEVlev
#SBATCH --output=output/process_@VAR_@LEVlev_%A_%a.o
#SBATCH --error=error/process_@VAR_@LEVlev_%A_%a.e
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --distribution=block:block
#SBATCH --account=n02-LDNDTP1
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --array=1-@NUM_RUNS

export OMP_NUM_THREADS=1 # Set number of threads to 1
export SRUN_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK # Propagate cpus-per-task from slurm to srun

# Export paths
export WORK=/mnt/lustre/a2fs-work2/work/n02/shared/jonnieb/
export BISICLES_BRANCH=$WORK/bisicles/master

# Load python, export paths for AMRfile, and activate python env for postprocessing
module load cray-python
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BISICLES_BRANCH/code/libamrfile
export PYTHONPATH=$PYTHONPATH:$BISICLES_BRANCH/code/libamrfile/python/AMRFile
source $WORK/env/bin/activate

# get run directory from slurm array ID
RUN_ID=$(printf "%02d" $SLURM_ARRAY_TASK_ID)
RUN_DIR=run${RUN_ID}

# process netcdf
python -u $WORK/lib/process_netcdf.py --lev @LEV @VAR ../$RUN_DIR/plot ../ncs
