# Installing BISICLES on archer2

These are instructions to build BISICLES on archer2. It includes steps to install BISICLES's third-party dependencies, [Chombo 3.2](https://commons.lbl.gov/display/chombo/Chombo+-+Software+for+Adaptive+Solutions+of+Partial+Differential+Equations) and [PETSc](https://petsc.org/release/). The instructions are borrowed heavily from the official [BISICLES build instructions](https://davis.lbl.gov/Manuals/BISICLES-DOCS/readme.html) with added detail by Matt Trevors and myself. 

Before you start, it's a good idea to add some helpful lines to your `.bashrc`. I recommend the following:

```shell
# load commonly used modules for BISICLES
module load PrgEnv-gnu
module load cray-python
module load cdo
module load cray-hdf5-parallel
module load cray-netcdf-hdf5parallel
module load nco
module load cray-fftw

# set bisicles and petsc directories
export WORK=/mnt/lustre/a2fs-work2/work/n02/shared/${USER} # yours may differ
export BISICLES_HOME=$WORK/bisicles
export PETSC_DIR=$BISICLES_HOME/petsc

# add amrfile and python to loader library path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BISICLES_HOME/master/code/libamrfile
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/cray/pe/python/3.9.13.1/lib

# python paths
export PYTHONPATH=$PYTHONPATH:/work/y07/shared/umshared/lib/python3.9
export PYTHONPATH=$PYTHONPATH:$BISICLES_HOME/bisicles/code/libamrfile/python/AMRFile

# fftw path
export FFTWDIR=/opt/cray/pe/fftw/default/x86_64

# BISICLES filetools
export NCTOAMR=$BISICLES_HOME/master/code/filetools/nctoamr2d.Linux.64.CC.ftn.OPT.MPI.GNU.ex
export FLATTEN=$BISICLES_HOME/master/code/filetools/flatten2d.Linux.64.CC.ftn.OPT.MPI.GNU.ex
export EXTRACT=$BISICLES_HOME/master/code/filetools/extract2d.Linux.64.CC.ftn.OPT.MPI.GNU.ex

# expand shell variables – not necessary, but generally useful on ARCHER2
shopt -s direxpand
```

Ensure that these are set by refreshing your bash settings:
```shell
source $HOME/.bashrc
```

Now make your main BISICLES directory, in which we will store Chombo, PETSc, and all of our BISICLES branches.

```bash
> mkdir -p $BISICLES_HOME
> cd $BISICLES_HOME
```

download source code for Chombo, BISICLES, and PETSC:

```bash
> git clone https://github.com/applied-numerical-algorithms-group-lbnl/Chombo_3.2.git Chombo
> git clone https://github.com/ggslc/bisicles-uob.git master
> git clone -b release https://gitlab.com/petsc/petsc.git petsc-src
```

## PETSc install

Temporarily set `PETSC_DIR` to `petsc-src` whilst we configure and install PETSc.

```bash
> export PETSC_DIR=$BISICLES_HOME/petsc-src
> cd $PETSC_DIR
```

There are several steps to installing PETSc, the first of which is to configure the install.

```bash
> ./configure --download-fblaslapack=yes --download-hypre=yes -with-x=0 --with-c++support=yes --with-mpi=yes --with-hypre=yes --prefix=$BISICLES_HOME/petsc --with-c2html=0 --with-ssl=0
```

After a few minutes and a lot of scrolling text, it should end with a message along the lines of:

```
Configure stage complete. Now build PETSc libraries with:
make PETSC_DIR=/mnt/lustre/a2fs-work2/work/n02/shared/jonnieb/bisicles/petsc-src PETSC_ARCH=arch-linux-c-debug all
```

Except with username and file paths specific to your setup. Copy and paste the line beginning `make PETSC_DIR=...` and execute.

After some more frantic printing to the console, you should see further instructions similar to:

```
Now to install the libraries do:
make PETSC_DIR=/mnt/lustre/a2fs-work2/work/n02/shared/jonnieb/bisicles/petsc-src PETSC_ARCH=arch-linux-c-debug install
```

Again, follow these instructions. This takes a few more minutes, but when it's done, the install is complete. Now change `PETSC_DIR` back to the definition as it appears in your `.bashrc`.

```bash
> export PETSC_DIR=$BISICLES_HOME/petsc
```

## Chombo setup

Chombo is configured through a file `Make.defs.local`, which sits in the `lib/mk/` subdirectory of Chombo. In `lib/mk/local`, you can see examples of such a setup for a number of different computing systems, including ARCHER, the predecessor to ARCHER2 (obviously). However, the standard release of Chombo is missing a `Make.defs` for ARCHER2, so we'll have to add our own. The easiest approach to this will be to copy the equivalent file from my own shared directory on ARCHER2. Start with:

```bash
> cp /work/n02/shared/jonnieb/bisicles/Chombo/lib/mk/local/Make.defs.archer2-system $BISICLES_HOME/Chombo/lib/mk/local
```

Then open `$BISICLES_HOME/Chombo/lib/mk/local/Make.defs.archer2-system` and change the line defining BISICLES_HOME to your own version of BISICLES_HOME. Lastly, make a symbolic link to `Make.defs.local` as follows:

```bash
> ln -s $BISICLES_HOME/Chombo/lib/mk/local/Make.defs.archer2-system $BISICLES_HOME/Chombo/lib/mk/Make.defs.local
```

These definitions are also inherited by BISICLES when compiling the main executable.

## Build BISICLES

BISICLES is more or less ready to compile out the box. However, if you plan to use the GIA functionality in BISICLES, you will need to add a flag so that the compiler doesn't skip the GIA sections of the source code. Probably the best place to include this will be in `$BISICLES_HOME/master/mk/Make.defs.archer2`. Add the line:

```bash
CPPFLAGS += -DBUELERGIA
```

`Make.defs.archer2` is (by default) symbolically linked to `Make.defs.ln01-6` in the same directory where `lnXX` are the ARCHER2 login nodes. These definitions are then inherited by the main BISICLES `Make.defs`, along with the Chombo definitions we configured earlier.

There are a few things to compile in BISICLES. The first is the main executable, done by:

```bash
> cd $BISICLES_HOME/master/code/exec2D
> make -j 4 all OPT=TRUE MPI=TRUE USE_PETSC=TRUE
```

You should now have the binary `driver2d.Linux.64.CC.ftn.OPT.MPI.PETSC.GNU.ex`. The `-j 4` uses 4 cores on the login node, which speeds up the process nicely. The other binaries to compile are the BISICLES filetools, which are used for a variety of purposes, e.g.:

- `flatten`: Flattens `.hdf5` files (BISICLES's adaptive-mesh outputs) to even-gridded netcdfs
- `nctoamr`: Converts in the opposite direction, from netcdfs to BISICLES-compatible `.hdf5`
- `extract`: Extracts some specified variables from a BISICLES `.hdf5` file to a new, smaller file

Compile all of these and more using:

```bash
> cd $BISICLES_HOME/master/code/filetools
> make -j 4 all OPT=TRUE MPI=TRUE USE_PETSC=TRUE
```

Lastly, the [BISICLES amrfile python module](https://davis.lbl.gov/Manuals/BISICLES-DOCS/libamrfile.html) is a useful tool for interacting directly with BISICLES `.hdf5` outputs in python. To use it, you just need to build the shared library `libamrfile.so`. It is also important to include the lines related to amrfile in your `.bashrc` so that archer2 can find the library, and you will need to set these again at the start of any slurm job that uses amrfile.

```bash
> cd $BISICLES_HOME/master/code/libamrfile
> make -j 4 libamrfile.so
```

Once that's done, you're good to go! If you ever want to install a different branch of BISICLES, you can do so easily using:

```bash
cd $BISICLES_HOME
git clone -b <branch_name> https://github.com/ggslc/bisicles-uob.git <branch_name>
```

and then repeat the steps in this subsection, activating GIA in `mk/`, building the main executable, filetool binaries, and amrfile shared library.
