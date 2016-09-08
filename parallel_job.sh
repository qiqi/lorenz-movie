#!/bin/bash
#SBATCH --job-name=lorenzMovie
#SBATCH --workdir=/master/home/niangxiu/lorenz-movie
#SBATCH --output=.out
#SBATCH --error=.err
#SBATCH --nodes=9
#SBATCH --ntasks-per-node=4
 
source /etc/profile.d/master-bin.sh
mpirun python lorenz.py
