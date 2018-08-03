#!/bin/bash

fit=/home/loco/edges/src/py/exp/fitSims.py
plot=/home/loco/edges/src/py/exp/plotSims2.py
folder=/home/loco/analysis/
f0=foreground_mini_simulation2_freq0.csv
f1=foreground_mini_simulation2_freq1.csv
f2=foreground_simulation2_freq0.csv
f3=foreground_simulation2_freq1.csv
poly=linpoly
phys=linphys
log=linlog

flags0=""
flags1="-s"
flags2="-n"
flags3="-s -n"

#source activate env_python3

#for file in $f0 $f1 $f2 $f3
#do
#  for model in $poly $phys $log
#  do   
#    for flags in "$flags0" #$flags1 $flags2 $flags3
#    do
#      python $fit $folder/$file --output $folder --model $model --fit -t 3 $flags
#      python $fit $folder/$file --output $folder --model $model --fit -t 4 $flags
#      python $fit $folder/$file --output $folder --model $model --fit -t 5 $flags
#      python $fit $folder/$file --output $folder --model $model --fit -t 6 $flags
#      python $fit $folder/$file --output $folder --model $model --fit -t 7 $flags
#    done
#  done
#done
#exit 1

statsfile=/home/loco/analysis/statistics2.txt

rm "$statsfile"
for terms in 3 4 5 6 7
do
  for model in $poly $log $phys 
  do
    for freq in 0 1
    do
      python $plot /home/loco/analysis/foreground_simulation2_freq"$freq"_fits_"$model"_sigFalse_noiseFalse_terms"$terms"_beta-2.5.csv >> $statsfile
    done
  done
done
 

