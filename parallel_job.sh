#!/bin/bash
#SBATCH --job-name=lorenzMovie-var-u0
#SBATCH --workdir=/master/home/niangxiu/lorenz-movie-var-u0/
#SBATCH --output=out.out
#SBATCH --error=err.err
#SBATCH --nodes=9
#SBATCH --ntasks-per-node=4
 
source /etc/profile.d/master-bin.sh
export PYTHONPATH=$PYTHONPATH:/master/home/niangxiu/.local/lib/python2.7/site-packages
mpirun python lorenz.py
