#!/bin/bash

exe=/home/loco/edges/src/py/exp/fitSims.py
folder=/home/loco/analysis/
f0=foreground_mini_simulation_freq0.csv
f1=foreground_mini_simulation_freq1.csv
poly=linpoly
phys=linphys
log=linlog

#The anaconda version is slower than the system version
#due to using openblas rather than intel_mkl.  So don't
#use anaconda.

#source activate env_python3


for file in $f0 $f1
do
  for model in $poly $phys #$log
  do
    python $exe $folder/$file --output $folder --model $model --grid -s
    #python $exe $folder/$file --output $folder --model $model --grid -s -n
  done
done

