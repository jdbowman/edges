#!/bin/bash

exe=/home/loco/edges/src/py/exp/plotMCMC.py
folder=/home/loco/analysis/mcmc
poly=linpoly
phys=linphys
log=linlog
files=$folder/*_temp00.csv

source activate env_python3

for file in $files
do
  python $exe $file --chains --corner
done



