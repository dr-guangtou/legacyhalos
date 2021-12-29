#! /bin/bash

# Shell script for running the various stages of the legacyhalos code using
# MPI+shifter at NERSC. Required arguments:
#   {1} stage [coadds, pipeline-coadds, ellipse, htmlplots]
#   {2} ncores [should match the resources requested.]

# Example: build the coadds using 64 MPI tasks with 4 cores per node (and therefore 64*4/32=8 nodes)

#salloc -N 8 -C haswell -A desi -L cfs,SCRATCH -t 04:00:00 --qos interactive --image=legacysurvey/legacyhalos:v0.1
#srun -n 64 -c 4 shifter --module=mpich-cle6 $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi.sh coadds 4 > hsclowz-coadds.log.1 2>&1 &
#srun -n 64 -c 4 shifter --module=mpich-cle6 $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi.sh ellipse 4 > hsclowz-ellipse.log.1 2>&1 &
#srun -n 64 -c 1 shifter --module=mpich-cle6 $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi.sh htmlplots 1 > hsclowz-htmlplots.log.1 2>&1 &

# Grab the input arguments--
stage=$1
ncores=$2

source $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-env

if [ $stage = "test" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi --help
elif [ $stage = "coadds" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi --coadds --nproc $ncores --mpi --verbose
elif [ $stage = "pipeline-coadds" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi --pipeline-coadds --nproc $ncores --mpi --verbose
elif [ $stage = "ellipse" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi --ellipse --nproc $ncores --mpi --verbose --sky-tests
elif [ $stage = "htmlplots" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/hsclowz/hsclowz-mpi --htmlplots --nproc $ncores --mpi --verbose
else
    echo "Unrecognized stage "$stage
fi
