#!/bin/bash

exe=/home/loco/edges/src/py/exp/fitSims.py
folder=/home/loco/analysis/
f0=foreground_mini_simulation2_freq0.csv
f1=foreground_mini_simulation2_freq1.csv
poly=linpoly
phys=linphys
log=linlog

#The anaconda version is slower than the system version
#due to using openblas rather than intel_mkl.  So don't
#use anaconda.

#source activate env_python3

#python $exe $folder/$f0 --output $folder --model linpoly --nterms 6 --grid -s -n
#python $exe $folder/$f0 --output $folder --model linpoly --nterms 7 --grid -s -n
#python $exe $folder/$f1 --output $folder --model linlog --nterms 4 --grid -s -n

#python $exe $folder/$f0 --output $folder --model linpoly --nterms 6 --grid -s
#python $exe $folder/$f0 --output $folder --model linpoly --nterms 7 --grid -s
#python $exe $folder/$f1 --output $folder --model linlog --nterms 4 --grid -s 

#python $exe $folder/$f0 --output $folder --model linlog --nterms 5 --grid -s -n           
#python $exe $folder/$f0 --output $folder --model linlog --nterms 5 --grid -s
#python $exe $folder/$f1 --output $folder --model linlog --nterms 5 --grid -s -n           
#python $exe $folder/$f1 --output $folder --model linlog --nterms 5 --grid -s

#exit 1

for file in $f0 $f1
do
  for model in $poly $log $phys
  do
    for terms in 5 3 4 6 7
    do
#      python $exe $folder/$file --output $folder --model $model --nterms $terms --grid -s
      python $exe $folder/$file --output $folder --model $model --nterms $terms --grid -s -n
    done
  done
done

