#!/bin/env python

'''
Script to extract data from hdf5 plotfiles and save it as a netcdf.

Usage: "python run_to_netcdf.py <run_directory> <variable>"
'''

import sys
import argparse
import numpy as np
import xarray as xr
from xarray import DataArray, Dataset
from pathlib import Path
from mpi4py import MPI # needed to run the MPI routines in amrio on archer2
from amr_setup import get_genpath # needed to import amrfile

genpath = get_genpath()
sys.path.append(genpath)
from amrfile import io as amrio

MAX_TIME = 2300     # cuts off data at any time above this value
FILL_VALUE = 0      # fill NaNs in netcdf with this value

# specs for encoding data.
specs = {
    'thickness'                      : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m'},
    'Z_surface'                      : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m'},
    'Z_base'                         : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m'},
    'Z_bottom'                       : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m'},
    'bTemp'                          : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'K'},
    'sTemp'                          : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'K'},
    'calvingFlux'                    : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':''},
    'calvingRate'                    : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':''},
    'dragCoef'                       : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':''},
    'viscosityCoef'                  : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':''},
    'iceFrac'                        : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':''},
    'basal_friction'                 : {'conversion':1.0, 'prec':1.00, 'dtype':'int32', 'units':''},
    'surfaceThicknessSource'         : {'conversion':1000.0, 'prec':1.0, 'dtype':'int32', 'units':'mm/yr'},
    'activeSurfaceThicknessSource'   : {'conversion':1000.0, 'prec':1.0, 'dtype':'int32', 'units':'mm/yr'},
    'basalThicknessSource'           : {'conversion':1000.0, 'prec':1.0, 'dtype':'int32', 'units':'mm/yr'},
    'activeBasalThicknessSource'     : {'conversion':1000.0, 'prec':1.0, 'dtype':'int32', 'units':'mm/yr'},
    'tillWaterDepth'                 : {'conversion':1000.0, 'prec':1.0, 'dtype':'int32', 'units':'mm'},
    'waterDepth'                     : {'conversion':1000.0, 'prec':1.0, 'dtype':'int32', 'units':'mm'},
    'mask'                           : {'conversion':1.0, 'prec':1.00, 'dtype':'int16', 'units':''}, 
    'yVel'                           : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m/yr'},
    'xVel'                           : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m/yr'},
    'ybVel'                          : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m/yr'},
    'xbVel'                          : {'conversion':1.0, 'prec':0.01, 'dtype':'int32', 'units':'m/yr'}
    }

def extract_field(variable: str, plotfile: Path, lev: int=0, order: int=0) -> Dataset:

    '''
    Extracts time and variable data from a .hdf5 plotfile and returns an xarray dataset

    :param variable: variable name
    :param plotfile: path to a BISICLES plotfile (plot.*.2d.hdf5)
    :param lev: level of refinement
    :param order: 

    :return time: time of plotfile
    :return ds: xarray dataset of variable
    '''

    # read hdf5
    amrID = amrio.load(plotfile)
    time = amrio.queryTime(amrID)
    lo, hi = amrio.queryDomainCorners(amrID, lev)
    y0, x0, field = amrio.readBox2D(amrID, lev, lo, hi, variable, order)
    # NB y, x are ordered this way here due to a quirk of how the BISICLES plotfiles organise their
    # axes. This order ensures, when we convert to netcdf, that x is on the horizontal axis and
    # y on the vertical.

    # convert into correct units
    conversion_factor = specs[variable]['conversion']
    field_in_units = np.asarray(field) * conversion_factor

    # make Dataset
    ds = Dataset({
        variable: DataArray(
            data = field_in_units,
            dims = ['x', 'y'],
            coords = {'x': x0, 'y': y0},
            attrs = {'units': specs[variable]['units']}
        )})
    amrio.free(amrID)

    return time, ds

def generate_netcdf(variable: str, plotdir: Path, outfile: Path, lev: int=0, overwrite: bool=False) -> None:

    '''
    Generates a netcdf of the given variable from the plotfiles of a BISICLES run.

    :param variable:    variable name
    :param plotdir:     path to plotfile directory
    :param outfile:     path for output netcdf
    :param lev:         level of refinement (0 by default, the most coarse resolution)
    :param overwrite:   will overwrite any existing netcdfs if True (False by default)
    '''

    # skip if file already exists
    if outfile.is_file() and not overwrite:
        print(f'{outfile} already exists.')
        return

    # Instantiate lists in which to store the time and data from each plotfile
    times = []
    timeslices = []
    plotfiles = sorted(plotdir.glob('plot.*.2d.hdf5'))
    total = len(plotfiles)
    for i, plotfile in enumerate(plotfiles):
        
        # print plotfile name and number to keep track of progress
        print(f'({i+1}/{total}) {plotfile.name}')

        # get datasets from plotfiles and associated time coordinates
        time, timeslice = extract_field(variable, str(plotfile), lev=lev)
        times.append(time)
        timeslices.append(timeslice)

    # concatenate along the time axis
    concatenated = xr.concat(timeslices, dim='time')
    ds = concatenated.assign_coords(time=times)
    ds = ds.sel(time=slice(0, MAX_TIME)) # trim off any leftover after time adjustments

    # get enconding info
    precision = specs[variable]['prec']
    dtype = specs[variable]['dtype']
    ds[variable].encoding.update({'zlib': True})
    
    # save netcdf
    ds.to_netcdf(outfile, encoding={variable: {
        'zlib'          : True, 
        'complevel'     : 6, 
        'dtype'         : dtype,
        'scale_factor'  : precision, 
        '_FillValue'    : FILL_VALUE
        }})

def get_outfile_path(variable: str, plotdir: Path, savedir: Path, lev: int) -> Path:

    '''
    Generates a name for an output netcdf in the format:

        <ensemble-name>_<run-name>_<variable>_<level-of-refinement>.nc

    NB This assumes that the directory structure for the ensemble is as follows:

        - ensemble home directory
            - run directory
                - plotfile directory (plotdir)
                    - plotfile 1
                    - plotfile 2
                    etc...

    :param variable:    variable name
    :param plotdir:     path to plotfile directory
    :param savedir:     path to a directory in which to save the netcdfs
    :param lev:         level of refinement (0 by default, the most coarse resolution)
    '''

    plotdir = plotdir.resolve()
    run = plotdir.parent
    ensemble = run.parent

    varsavedir = savedir / lev / variable 
    varsavedir.mkdir(parents=True, exist_ok=True)

    outpath = varsavedir / f'{ensemble.name}_{run.name}_{variable}_{lev}lev.nc'

    return outpath

def main(args) -> None:

    '''
    When called from the command line, this script takes three arguments:

        - The variable to process
        - The plotdile directory to work on
        - The save directory in which the netcdfs will be saved

    Additionally, the option --lev can be called with the level of refinement with
    which to generate the netcdfs.

    main() takes those arguments, generates a path for the output netcdf based on the
    ensemble directory structure [see get_outfile_path()], then processes and saves
    the netcdf.
    '''

    lev = args.lev if args.lev else 0
    outfile_path = get_outfile_path(args.variable, args.plotdir, args.savedir, lev)
    generate_netcdf(args.variable, args.plotdir, outfile_path, lev=lev)


if __name__== '__main__':
    parser = argparse.ArgumentParser(
        description="Process inputs and options"
        )

    # add arguments
    parser.add_argument("variable", type=str, help="variable name") 
    parser.add_argument("plotdir", type=str, help="Path to z_base netcdfs")
    parser.add_argument("savedir", type=str, help="Path to save directory")

    # add optional arguments
    parser.add_argument("--lev", type=int, help="level of refinement")

    args = parser.parse_args()
    main(args)

                           
