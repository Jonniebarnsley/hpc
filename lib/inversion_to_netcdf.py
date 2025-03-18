import argparse
from pathlib import Path
from process_netcdf import generate_netcdf

def main(args) -> None:

    lev = args.lev if args.lev else 0
    ctrl_dir = Path(args.ctrl_dir)
    outfile_path = Path(args.outfile_path)
    generate_netcdf(args.variable, ctrl_dir, outfile_path, lev=lev)

if __name__== '__main__':
    parser = argparse.ArgumentParser(
        description="Process inputs and options"
        )

    # add arguments
    parser.add_argument("variable", type=str, help="variable name") 
    parser.add_argument("ctrl_dir", type=str, help="Path to netcdfs")
    parser.add_argument("outfile_path", type=str, help="Path for output netcdf")

    # add optional arguments
    parser.add_argument("--lev", type=int, help="level of refinement")

    args = parser.parse_args()
    main(args)