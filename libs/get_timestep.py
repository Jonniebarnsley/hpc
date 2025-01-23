import sys
from mpi4py import MPI # needed to run the MPI routines in amrio
from amr_setup import get_genpath # needed to import amrfile

genpath = get_genpath()
sys.path.append(genpath)
from amrfile import io as amrio

def get_timestep(plotfile):

    amrID  = amrio.load(plotfile)
    time = amrio.queryTime(amrID)

    return time

def main():
    if len(sys.argv) != 2:
        print('Usage: python get_timestep.py <plotfile>')
    else:
        plotfile = sys.argv[1]
        try:
            ts = get_timestep(plotfile)
            print(ts)
        except Exception as e:
            print(f'Error: {e}')
        
if __name__ == '__main__':
    main()