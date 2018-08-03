#!/bin/bash

exe=/home/loco/edges/src/py/exp/plotSims.py
exe2=/home/loco/edges/src/py/exp/plotSims2.py

#The anaconda version is slower than the system version
#due to using openblas rather than intel_mkl.  So don't
#use anaconda.

source activate env_python3


f0=foreground_mini_simulation_freq0_gridsearch1004400_linlog_sigTrue_noiseFalse_covFalse_terms5_beta-2.5.csv
f1=foreground_mini_simulation_freq0_gridsearch1004400_linlog_sigTrue_noiseTrue_covFalse_terms5_beta-2.5.csv
f2=foreground_mini_simulation_freq0_gridsearch1004400_linpoly_sigTrue_noiseFalse_covFalse_terms6_beta-2.5.csv
f3=foreground_mini_simulation_freq0_gridsearch1004400_linpoly_sigTrue_noiseFalse_covFalse_terms7_beta-2.5.csv
f4=foreground_mini_simulation_freq0_gridsearch1004400_linpoly_sigTrue_noiseTrue_covFalse_terms6_beta-2.5.csv
f5=foreground_mini_simulation_freq0_gridsearch1004400_linpoly_sigTrue_noiseTrue_covFalse_terms7_beta-2.5.csv
f6=foreground_mini_simulation_freq1_gridsearch1004400_linlog_sigTrue_noiseFalse_covFalse_terms4_beta-2.5.csv
f7=foreground_mini_simulation_freq1_gridsearch1004400_linlog_sigTrue_noiseFalse_covFalse_terms5_beta-2.5.csv
f8=foreground_mini_simulation_freq1_gridsearch1004400_linlog_sigTrue_noiseTrue_covFalse_terms4_beta-2.5.csv
f9=foreground_mini_simulation_freq1_gridsearch1004400_linlog_sigTrue_noiseTrue_covFalse_terms5_beta-2.5.csv


# Plot input foreground models for full frequency range
file="foreground_mini_simulation2_freq0.csv"
python $exe2 /home/loco/analysis/$file --spec

# Plot residual RMS for foreground-only fits for N=5 case
folder=/home/loco/analysis/linfits
file="foreground_simulation2_freq{}_fits_{}_sigFalse_noise{}_terms5_beta-2.5.csv"
#python $exe $folder/$file --dualhist --label 'Residual RMS [K]' --param 5 --bins 0 0.05 51
python $exe $folder/$file --dualhist --label 'Residual RMS [K]' --param 5 --bins 0 0.2 51
file="foreground_mini_simulation2_freq{}_fits_{}_sigFalse_noise{}_terms5_beta-2.5.csv"
#python $exe $folder/$file --dualhist --label 'Residual RMS [K]' --param 5 --bins 0 0.05 51

# Plot signal parameter best-fits for N=5 case
folder=/home/loco/analysis/grid
file="foreground_mini_simulation2_freq{}_gridsearch1004400_{}_sigTrue_noise{}_covFalse_terms5_beta-2.5.csv"
#python $exe $folder/$file --dualhist --label 'Best-fit center frequency [MHz]' --param 5 --bins 59.5 90.5 32 --value 80
#python $exe $folder/$file --dualhist --label 'Best-fit width [MHz]' --param 6 --bins 0.5 40.5 41 --value 20
#python $exe $folder/$file --dualhist --label 'Best-fit tau' --param 7 --bins 0.5 10.5 11 --value 7
#python $exe $folder/$file --dualhist --label 'Best-fit amplitude [K]' --param 8 --bins -2.025 2.025 82 --value -0.5

# Plot signal paramter amplitude best-fit for all N cases
#for terms in 4 5 6 7
#do
#  param=`expr $terms + 3`
#  file="foreground_mini_simulation2_freq{}_gridsearch1004400_{}_sigTrue_noise{}_covFalse_terms"$terms"_beta-2.5.csv"
#  python $exe $folder/$file --hist --label 'Best-fit amplitude [K]' --param $param --bins -2.025 2.025 82 --value -0.5
#  python $exe $folder/$file --spec
#done




