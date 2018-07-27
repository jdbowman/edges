#!/bin/bash

fit=/home/loco/edges/src/py/exp/fitSims.py
plot=/home/loco/edges/src/py/exp/plotSims2.py
folder=/home/loco/analysis/
f0=foreground_mini_simulation_freq0.csv
f1=foreground_mini_simulation_freq1.csv
f2=foreground_simulation_freq0.csv
f3=foreground_simulation_freq1.csv
poly=linpoly
phys=linphys
log=linlog

#source activate env_python3

#for file in $f0 $f1 $f2 $f3
#do
#  for model in $poly $log
#  do
#    python $fit $folder/$file --output $folder --model $model --fit -t 3 &
#    python $fit $folder/$file --output $folder --model $model --fit -t 4 &
#    python $fit $folder/$file --output $folder --model $model --fit -t 5 &
#    python $fit $folder/$file --output $folder --model $model --fit -t 6 &
#    python $fit $folder/$file --output $folder --model $model --fit -t 7 &
        
    #python $fit $folder/$file --output $folder --model $model --fit -s
    #python $fit $folder/$file --output $folder --model $model --fit -n
    #python $fit $folder/$file --output $folder --model $model --fit -s -n
#  done
#done


statsfile=/home/loco/analysis/statistics.txt

rm "$statsfile"
for terms in 3 4 5 6 7
do
  for model in $poly $log
  do
    for freq in 0 1
    do
      python $plot /home/loco/analysis/foreground_simulation_freq"$freq"_fits_"$model"_sigFalse_noiseFalse_terms"$terms"_beta-2.5.csv >> $statsfile
    done
  done
done
 

