import os
from pathlib import Path

# The amrfile python package comes with BISICLES (https://github.com/ggslc/bisicles-uob) and is used
# to extract data from the hdf5 files that BISICLES produces as output. To import amrfile, we first
# need to add the path in which it is stored to the PYTHONPATH environment variable.

# The following lines require that the BISICLES_HOME environment variable is set to the BISICLES home
# directory. You may also need to change BISICLES_VERSION_NAME below to match your installation.

def get_genpath() -> Path:

    BISICLES_VERSION_NAME = 'ocean_conn'
    BISICLES_HOME = os.environ.get('BISICLES_HOME')

    if BISICLES_HOME is None:
        raise EnvironmentError("BISICLES_HOME environment variable is not set.")

    genpath = Path(BISICLES_HOME) / BISICLES_VERSION_NAME / 'code/libamrfile/python/AMRFile'
    amrfile = genpath / 'amrfile'
    if not amrfile.is_dir():
        raise FileNotFoundError(f'Directory not found: {amrfile}')
    
    return genpath
    

    

