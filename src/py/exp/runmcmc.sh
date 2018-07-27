#!/bin/bash

exe=/home/loco/edges/src/py/exp/doMCMC.py
infile=/home/loco/analysis/figure1_plotdata.csv

source activate env_python3

for fmin in 63
do
  for model in linpoly linphys linlog explog
  do
    python $exe $infile --model $model --niter 300000 --nwalker 100 -p 10 --fmin $fmin 
  done
done




