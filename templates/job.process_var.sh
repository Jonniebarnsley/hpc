#!/bin/bash
#SBATCH --job-name=process_@VAR_@NAME
#SBATCH -o output/process_@VAR.%j.o
#SBATCH -e error/process_@VAR.%j.e
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --time=02:00:00
#SBATCH --qos=standard
#SBATCH --account=n02-LDNDTP1
#SBATCH --hint=nomultithread
#SBATCH --distribution=block:block

# set paths
export WORK=/mnt/lustre/a2fs-work2/work/n02/shared/jonnieb/
export BISICLES=$WORK/bisicles/master

# load python
module load cray-python
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BISICLES/code/libamrfile
export PYTHONPATH=$PYTHONPATH:$BISICLES/code/libamrfile/python/AMRFile
source $WORK/env/bin/activate

# load some helpful functions
source $WORK/lib/utils.sh

start=$(date +%s)
echo Start time is `date`

cd $SLURM_SUBMIT_DIR
python -u $WORK/lib/process_netcdf.py @VAR @PLOTDIR @NCDIR

end=$(date +%s)
echo End time is `date`
echo Time elapsed: $(time_elapsed $start $end)

