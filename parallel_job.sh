#!/bin/bash
#SBATCH --job-name=lorenzMovie
#SBATCH --workdir=/master/home/niangxiu/lorenz-movie
#SBATCH --output=out.out
#SBATCH --error=err.err
#SBATCH --nodes=18
#SBATCH --ntasks-per-node=4
 
source /etc/profile.d/master-bin.sh
export PYTHONPATH=$PYTHONPATH:/master/home/niangxiu/.local/lib/python2.7/site-packages
mpirun python lorenz.py
