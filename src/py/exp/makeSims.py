import numpy as np
import csv
import sys
sys.path.append('..');
import models


    
# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():

  # Define the parameters for the run
  outputDir = '/home/loco/analysis/';
  dataFile = '/home/loco/analysis/figure1_plotdata.csv';
  vc = 75;
    
  # Load public EDGS data from Bowman et al. 2018 Figure 1
  data = np.genfromtxt(dataFile, delimiter=',', skip_header=1);
  f = data[:,0];
  w = data[:,1];
  d = data[:,2];
  
  # Extract frequency coordinates from the data file for small and large subbands
  v = [data[(data[:,1]>0),0], data[(data[:,0]>63) & (data[:,0]<99),0]];
   
  # --------------------------------------------------------------------------- #
  # Make a set of simulated foreground realizations 
  # --------------------------------------------------------------------------- #
   
  # Sample the model parameters in a multi-dimensional grid with points at the 
  # following parameter values:
  steps = [
    [1500, 1750, 2000], 
    [-2.6, -2.55, -2.5, -2.45, -2.4], 
    [-0.1, -0.05, 0, 0.05, 0.1],
    [-0.1, -0.05, 0, 0.05, 0.1],
    [-0.1, -0.05, 0, 0.05, 0.1],
    [0, 0.005, 0.05],
    [0, 500, 750, 1000]];
  
  steps_mini = [
    [1500, 1750], 
    [-2.6, -2.5, -2.4], 
    [-0.1, 0, 0.1],
    [-0.1, 0, 0.1],
    [-0.1, 0, 0.1],
    [0, 0.005],
    [0, 1000]];
      
  # Generate all parmeter grid points
  params = models.populateGrid(steps);
  params_mini = models.populateGrid(steps_mini);
  
  # Generate the foreground realizations
  set = [models.fullSet(x, vc, params[:-2,:], params[-2:,:]) for x in v];
  set_mini = [models.fullSet(x, vc, params_mini[:-2,:], params_mini[-2:,:]) for x in v];
  
  # --------------------------------------------------------------------------- #
  # Write realizations to disk
  # --------------------------------------------------------------------------- #
  
  # Do it for each frequency range
  for i in range(len(v)):

    # Open file for output
    filename = "{}/foreground_simulation2_freq{}.csv".format(outputDir, i);
    with open(filename, "w") as csvFile:
      csvWriter = csv.writer(csvFile);
       
      # Write header
      csvWriter.writerow(['b0', 'b1', 'b2', 'b3', 'b4', 'tau', 'Te'] + ["{0:8.6f}".format(n) for n in v[i]]);

      # Write data
      for j in range(params.shape[1]):
        csvWriter.writerow(np.concatenate( (np.array(params[:,j]), set[i][:,j])) );
          
    # Open file for output
    filename = "{}/foreground_mini_simulation2_freq{}.csv".format(outputDir, i);
    with open(filename, "w") as csvFile:
      csvWriter = csv.writer(csvFile);
       
      # Write header
      csvWriter.writerow(['b0', 'b1', 'b2', 'b3', 'b4', 'tau', 'Te'] + ["{0:8.6f}".format(n) for n in v[i]]);
      
      # Write data
      for j in range(params_mini.shape[1]):
        csvWriter.writerow(np.concatenate( (params_mini[:,j], set_mini[i][:,j]) ));
       
        
        
  
  
  
# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();
