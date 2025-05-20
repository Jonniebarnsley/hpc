import sys
import argparse
import numpy as np
from mpi4py import MPI
from xarray import Dataset, DataArray

# import amrfile – requires PYTHONPATH and LD_LIBRARY_PATH correctly set
from amrfile import io as amrio

def convert_C(C: DataArray, xVel: DataArray, yVel: DataArray, m: int=1) -> DataArray:

    '''
    Inverse problem is solved with Weertman exponent m = 1. We would like to 
    convert the inverted field for Weertman coefficient C into an equivalent 
    field for any m such that friction is unchanged upon initialisation.

    This can be done by solving the equation that equates both friction regimes.

    C|u| = C_m|u|^m
    C_m = C|u|^(1-m)
    '''

    print(f'Converting C into equivalent field for m={m}...')
    speed = np.hypot(xVel, yVel)
    C_m = C * (1.0 + speed**(1.0-m)) # regularising term to prevent C_m = 0

    return C_m

def extract_data(file: str, lev: int=3, order: int=0) -> Dataset:
   
    attrs = {
            'thickness' : {'long_name': 'Ice thickness', 'units': 'm'},
            'Z_base'    : {'long_name': 'Bed elevation', 'units': 'm'},
            'Cwshelf'   : {'long_name': 'Weertman friction coefficient (m=1)', 'units': 'Pa·m⁻¹·s'},
            'muCoef'    : {'long_name': 'Viscosity coefficient'},
            'xVelb'     : {'long_name': 'Basal x-velocity', 'units': 'm/a'},
            'yVelb'     : {'long_name': 'Basal y-velocity', 'units': 'm/a'}
            }
            
    # load hdf5 file
    amrID = amrio.load(file)
    lo, hi = amrio.queryDomainCorners(amrID, lev)
    
    # read data
    data = {}
    varnames = ['thickness', 'Z_base', 'Cwshelf', 'muCoef', 'xVelb', 'yVelb']
    for var in varnames:
        print(f'extracting {var}...')
        x0, y0, field = amrio.readBox2D(amrID, lev, lo, hi, var, order)
        data[var] = (['y', 'x'], field, attrs[var])
    
    # make dataset
    ds = Dataset(
            data,
            coords = {'x': x0, 'y': y0},
            )

    amrio.free(amrID)
    
    return ds

def main(args) -> None:

    infile = args.infile
    outfile = args.outfile
    lev = args.lev

    ds = extract_data(infile, lev=lev)
    
    if args.m:
        ds['C_m'] = convert_C(ds.Cwshelf, ds.xVelb, ds.yVelb, args.m)
    else:
        ds['C_m'] = ds['Cwshelf']
    
    ds['C_m'].attrs['long_name'] = f'Weertman coefficient (m={args.m if args.m else 1})'
    ds['C_m'].attrs['units'] = 'Pa·m⁻¹·s'  # or appropriate
    
    print(f'saving to {outfile}...')
    encoding = {
        var: {
            'zlib': True,          # enables compression
            'complevel': 4,        # compression level (1–9)
            'dtype': 'float32',    # reduce file size if precision allows
            '_FillValue': None     # avoids auto-inserting NaNs as fill values
        }
        for var in ds.data_vars
    }
    ds.to_netcdf(outfile, encoding=encoding)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process inputs and options")

    # add arguments
    parser.add_argument("infile", type=str, help="path to ctrl.*.hdf5 file")
    parser.add_argument("outfile", type=str, help="path to output netcdf")

    # add optional arguments
    parser.add_argument("-m", type=float, help="value of Weertman exponent")
    parser.add_argument("--lev", type=int, default=3, help="max level of refinement")

    args = parser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')

