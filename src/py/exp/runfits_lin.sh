#!/bin/bash

fit=/home/loco/edges/src/py/exp/fitSims.py
folder=/home/loco/analysis/
f0=foreground_mini_simulation_freq0.csv
f1=foreground_mini_simulation_freq1.csv
f2=foreground_simulation_freq0.csv
f3=foreground_simulation_freq1.csv
poly=linpoly
phys=linphys
log=linlog

#source activate env_python3

for file in $f0 $f1 $f2 $f3
do
  for model in $poly $phys $log
  do
    python $fit $folder/$file --output $folder --model $model --fit
    python $fit $folder/$file --output $folder --model $model --fit -s
    python $fit $folder/$file --output $folder --model $model --fit -n
    python $fit $folder/$file --output $folder --model $model --fit -s -n
  done
done



