#! /bin/bash

# Shell script for running the various stages of the legacyhalos code using
# MPI+shifter at NERSC. Required arguments:
#   {1} stage [coadds, pipeline-coadds, ellipse, htmlplots]
#   {2} ncores [should match the resources requested.]

# Example: build the coadds using 16 MPI tasks with 8 cores per node (and therefore 16*8/32=4 nodes)

#salloc -N 4 -C haswell -A desi -L cfs,SCRATCH -t 04:00:00 --qos realtime --image=legacysurvey/legacyhalos:v0.0.2 --exclusive
#srun -n 4 -c 32 shifter --module=mpich-cle6 /global/cscratch1/sd/ioannis/largegalaxies-customredux/SGA-customredux-mpi.sh coadds 32 > coadds-customredux.log.1 2>&1 &

# Grab the input arguments--
stage=$1
ncores=$2

#source $LEGACYHALOS_CODE_DIR/bin/SGA/SGA-customredux-env
source /global/cscratch1/sd/ioannis/largegalaxies-customredux/SGA-customredux-env # hack

maxmem=134217728 # Cori/Haswell = 128 GB (limit the memory per job).
grep -q "Xeon Phi" /proc/cpuinfo && maxmem=100663296 # Cori/KNL = 98 GB
let usemem=${maxmem}*${ncores}/32

if [ $stage = "test" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/SGA/SGA-mpi --help
elif [ $stage = "coadds" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/SGA/SGA-mpi --coadds --nproc $ncores --mpi --verbose --d25max 17.0
elif [ $stage = "pipeline-coadds" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/SGA/SGA-mpi --pipeline-coadds --nproc $ncores --mpi --verbose
elif [ $stage = "ellipse" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/SGA/SGA-mpi --ellipse --nproc $ncores --mpi --verbose --d25max 2
elif [ $stage = "htmlplots" ]; then
    time python $LEGACYHALOS_CODE_DIR/bin/SGA/SGA-mpi --htmlplots --nproc $ncores --mpi --verbose
else
    echo "Unrecognized stage "$stage
fi
