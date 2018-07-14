import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import csv
import os
import errno
import sys
sys.path.append('..');
import models

# --------------------------------------------------------------------------- #
# Parallel processing unit job
# --------------------------------------------------------------------------- #
def processJob(x, data, dataCov, foregroundComponents, signalFunction, signalTrials, filename, i):

  foregroundFits, residualRMSs = models.searchTrials(data[:,i], 
                                                     dataCov, 
                                                     foregroundComponents, 
                                                     x, 
                                                     signalFunction, 
                                                     signalTrials);
  index = np.argmin(residualRMSs);
    
  row = [];
  row.append(index);
  row.append(residualRMSs[index]);
  for item in foregroundFits[:,index]:
    row.append(item);
  for item in signalTrials[:,index]:
    row.append(item);
  
  with open(filename, "a") as csvFile:
    csvWriter = csv.writer(csvFile, lineterminator='\n');
    csvWriter.writerow(row);
    
  return row;


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():

  # Define the parameters for the run
  
#  outputBase = 'G:/My Drive/EDGES/mcmc/run2';
#  dataFile = 'G:/My Drive/Publications/Papers/2017_EDGES_Low/PublicData/figure1_plotdata.csv';

  outputBase = '/home/loco/analysis/run3';
  dataFile = '/home/loco/analysis/figure1_plotdata.csv';
  njobs = 12;
  vc = 75;
  beta = -2.5;
  nterms = 5;
    
  # Load public EDGS data from Bowman et al. 2018 Figure 1
  data = np.genfromtxt(dataFile, delimiter=',', skip_header=1);
  f = data[:,0];
  w = data[:,1];
  d = data[:,2];
  
  # Extract frequency coordinates from the data file for small and large subbands
  v = [data[(data[:,1]>0),0], data[(data[:,0]>63) & (data[:,0]<99),0]];
  
  # Extract the data for the same ranges
  d = [data[(data[:,1]>0),2], data[(data[:,0]>63) & (data[:,0]<99),2]];
  
  # Estimated thermal noise;
  n = [0.025 * np.ones(d[i].size) for i in range(len(v))];
  
  # --------------------------------------------------------------------------- #
  # Make a set of simulated foreground realizations 
  # --------------------------------------------------------------------------- #
   
  # Sample the model parameters in a multi-dimensional grid with points at the 
  # following parameter values:
  steps = [
    [1250, 1500, 1750], 
    [-2.6, -2.55, -2.5, -2.45, -2.4], 
    [-0.1, -0.05, 0, 0.05, 0.1],
    [-0.1, -0.05, 0, 0.05, 0.1],
    [-0.1, -0.05, 0, 0.05, 0.1],
    [0, 0.05, 0.1],
    [0, 500, 750, 1000]];
  
  steps_mini = [
    [1500, 1750], 
    [-2.6, -2.5, -2.4], 
    [-0.1, 0, 0.1],
    [-0.1, 0, 0.1],
    [-0.1, 0, 0.1],
    [0, 0.1],
    [0, 1000]];
      
  sig = [80, 20, 7, -0.5];
  steps_sig = [
    np.linspace(55, 100, 10), 
    np.linspace(5, 50, 10),
    np.linspace(1, 9, 5),
    np.linspace(-2, 2, 21)];
      
  # Generate all parmeter grid points
  params = models.populateGrid(steps);
  params_mini = models.populateGrid(steps_mini);
  params_sig = models.populateGrid(steps_sig);
  
  # Generate the realizations
  set = [models.fullSet(x, vc, params[:-2,:], params[-2:,:]) for x in v];
  set_mini = [models.fullSet(x, vc, params_mini[:-2,:], params_mini[-2:,:]) for x in v];
  
  # Make a version of the realizations with a simulated signal feature
  set_sig = [np.add(set_mini[i].transpose(), models.flattenedGaussian(v[i], sig)).transpose() for i in range(len(v))];
  
  # Append the actual data to the end of the foreground-only realization set
  set = [np.hstack([set[i], d[i].reshape([v[i].size,1])]) for i in range(len(v))];
  set_mini = [np.hstack([set_mini[i], d[i].reshape([v[i].size,1])]) for i in range(len(v))];
  
  # Generate the vector components of the models we'll fit
  foregroundComponents = [];
  foregroundComponents.append([models.linearPolynomialComponents(x,vc,nterms, beta=beta) for x in v]);
  foregroundComponents.append([models.linearPhysicalComponents(x, vc) for x in v]);
  
  
  # --------------------------------------------------------------------------- #
  # Fit the simulated/real data
  # --------------------------------------------------------------------------- #
  
  fits = [models.fitLinear(x, y) for x,y in zip(set, componentsPoly)];
  estimatesPoly = [x[0] for x in fits];
  rmsPoly = [x[1] for x in fits];
  diffPoly = [set[i] - componentsPoly[i].dot(estimatesPoly[i]) for i in range(0,len(set))];
  
  fits = [models.fitLinear(x, y) for x,y in zip(set, componentsPhys)];
  estimatesPhys = [x[0] for x in fits];
  rmsPhys = [x[1] for x in fits];
  diffPhys = [set[i] - componentsPhys[i].dot(estimatesPhys[i]) for i in range(0,len(set))];
  
  # Estimate the equivalent RMS with EDGES thermal noise
  rmsNoise = 0.025;
  rmsPolyNoise = [np.sqrt(x**2 + rmsNoise**2) for x in rmsPoly];
  rmsPhysNoise = [np.sqrt(x**2 + rmsNoise**2) for x in rmsPhys];
  
  
  # --------------------------------------------------------------------------- #
  # Fit the simulated data that includes the fake signal feature
  # --------------------------------------------------------------------------- #
  noiseCov = [np.diag(x*x) for x in n];  
  rcvSig = [[np.zeros([params_sig.shape[0], set_sig[i].shape[1]]) for i in range(len(v))] for j in range(len(foregroundComponents))];
  rcvRMS = [[np.zeros([1, set_sig[i].shape[1]]) for i in range(len(v))] for j in range(len(foregroundComponents))];  
  
  for k in range(len(v)):
    for j in range(len(foregroundComponents)):
      
      # Filename for CSV output
      filename = "{}_gridsearch_freq{}_model{}.txt".format(outputBase, k, j);  
      
      # Delete any existing file
      try:
        os.remove(filename)
      except OSError:
        pass
              
      # Start the parallel jobs
      results = Parallel(n_jobs=njobs, verbose=100)(delayed(processJob)(v[k], set_sig[k],
               noiseCov[k], 
               foregroundComponents[j][k], 
               models.flattenedGaussian, 
               params_sig, 
               filename, 
               i) 
               for i in range(params_mini.shape[1]));
  
  # --------------------------------------------------------------------------- #
  # Read back in simulated signal fit results
  # --------------------------------------------------------------------------- #    
  for k in range(len(v)):
    for j in range(len(foregroundComponents)):   

      # Filename for CSV input
      filename = "{}_gridsearch_freq{}_model{}.txt".format(outputBase, k, j);
      
      with open(filename, "r") as csvFile:
        csvReader = csv.reader(csvFile);
        nrow = 0;
        for row in csvReader:
          recoveredSig[j][k][:,nrow] = row[-4:];
          recoveredRMS[j][k][nrow] = row[1];
          nrow = nrow + 1;
          
      
  
  # --------------------------------------------------------------------------- #
  # Plot the results
  # --------------------------------------------------------------------------- #
  
  plt.figure(1);
  plt.clf();
  lw1=2;
  lw2=2;
  plt.plot(rmsPhys[0][-1]*np.array([1.0, 1.0]), np.array([1500, 8000]), 'k--', linewidth=lw1);
  plt.plot(rmsPhys[1][-1]*np.array([1.0, 1.0]), np.array([1500, 8000]), 'g:', linewidth=lw1);
  plt.plot(rmsPoly[0][-1]*np.array([1.0, 1.0]), np.array([1500, 8000]), 'r-', linewidth=lw1);
  plt.plot(rmsPoly[1][-1]*np.array([1.0, 1.0]), np.array([1500, 8000]), 'b-', linewidth=lw1);
  plt.hist(rmsPhysNoise[0], bins=np.logspace(-2,-1,50), density=False, histtype='step', edgecolor='black', linewidth=lw2, linestyle='dashed', alpha=1);
  plt.hist(rmsPhysNoise[1], bins=np.logspace(-2,-1,50), density=False, histtype='step', edgecolor='green', linewidth=lw2, linestyle='dotted', alpha=1);
  plt.hist(rmsPolyNoise[0], bins=np.logspace(-2,0,100), density=False, histtype='stepfilled',facecolor='red', linewidth=lw2, alpha=0.5);
  plt.hist(rmsPolyNoise[1], bins=np.logspace(-2,-1,50), density=False, histtype='stepfilled',facecolor='blue', linewidth=lw2, alpha=0.3);
  ax = plt.gca();
  ax.set_xscale('log');
  ax.set_yscale('log');
  plt.ylim([3,1e5]);
  plt.xlim([1e-2, 4e-1]);
  plt.xlabel('RMS residual [K]');
  plt.ylabel('Samples');
  plt.legend(['50-100 MHz linphys', '63-99 MHz linphys', '50-100 MHz poly', '63-99 MHz poly'], loc='upper right');
  plt.title('Histogram of RMS residual \nto simulated foregrounds plus noise');
  plt.show();
  
  
  plt.figure(2);
  plt.clf();
  lw1=2;
  lw2=2;
  plt.plot(np.sqrt(rmsPhys[0][-1]**2 - 0.025**2)*np.array([1.0, 1.0]), np.array([4500, 5500]), 'k--', linewidth=lw1);
  plt.plot(np.sqrt(rmsPhys[1][-1]**2 - 0.025**2)*np.array([1.0, 1.0]), np.array([4500, 5500]), 'g:', linewidth=lw1);
  plt.plot(np.sqrt(rmsPoly[0][-1]**2 - 0.025**2)*np.array([1.0, 1.0]), np.array([4500, 5500]), 'r-', linewidth=lw1);
  plt.plot(np.sqrt(rmsPoly[1][-1]**2 - 0.025**2)*np.array([1.0, 1.0]), np.array([4500, 5500]), 'b-', linewidth=lw1);
  plt.hist(rmsPhys[0], bins=np.logspace(-5,0,50), density=False, histtype='step', edgecolor='black', linewidth=lw2, linestyle='dashed', alpha=1);
  plt.hist(rmsPhys[1], bins=np.logspace(-5,0,50), density=False, histtype='step', edgecolor='green', linewidth=lw2, linestyle='dotted', alpha=1);
  plt.hist(rmsPoly[0], bins=np.logspace(-4,0,40), density=False, histtype='stepfilled',facecolor='red', linewidth=lw2, alpha=0.5);
  plt.hist(rmsPoly[1], bins=np.logspace(-5,0,50), density=False, histtype='stepfilled',facecolor='blue', linewidth=lw2, alpha=0.5);
  ax = plt.gca();
  ax.set_xscale('log');
  #ax.set_yscale('log');
  plt.ylim([0,6000]);
  plt.xlim([3e-6, 1]);
  plt.xlabel('RMS residual [K]');
  plt.ylabel('Samples');
  plt.legend(['50-100 MHz linphys', '63-99 MHz linphys', '50-100 MHz poly', '63-99 MHz poly'], loc='upper left');
  plt.title('Histogram of RMS residual to simulated foregrounds');
  plt.show();
  
  plt.figure(3);
  plt.clf();
  plt.plot(v[0], diffPhys[0][:,-1]);
  plt.plot(v[1], diffPhys[1][:,-1]);
  plt.plot(v[0], diffPoly[0][:,-1]);
  plt.plot(v[1], diffPoly[1][:,-1]);
  print(rmsPhys[0][-1])
  print(rmsPhys[1][-1])
  print(rmsPoly[0][-1])
  print(rmsPoly[1][-1])
  plt.show();

  plt.figure(4);
  plt.clf();
  plt.hist(rcvSig[0][1][3,0:648], bins=np.linspace(-2.1,2.1,22), density=False, histtype='stepfilled',facecolor='blue', linewidth=lw2, alpha=0.5); 
  plt.hist(rcvSig[0][0][3,0:648], bins=np.linspace(-2.1,2.1,22), density=False, histtype='stepfilled',facecolor='red', linewidth=lw2, alpha=0.75);
  plt.plot([-0.5, -0.5], [0, 500], 'k:');
  plt.xlabel("Best fit amplitude [K]");
  plt.ylabel("Samples");
  plt.legend(["True (-0.5 K)", "63-99 MHz poly", "50-100 MHz poly"]);
  plt.ylim([0, 450]);
  plt.savefig("{}_hist_recovered_amp_poly.png".format(outputBase));

  plt.figure(5);
  plt.clf();
  plt.hist(rcvSig[1][1][3,0:648], bins=np.linspace(-2.1,2.1,22), density=False, histtype='stepfilled',facecolor='blue', linewidth=lw2, alpha=0.5); 
  plt.hist(rcvSig[1][0][3,0:648], bins=np.linspace(-2.1,2.1,22), density=False, histtype='stepfilled',facecolor='red', linewidth=lw2, alpha=0.75);
  plt.plot([-0.5, -0.5], [0, 500], 'k:');
  plt.xlabel("Best fit amplitude [K]");
  plt.ylabel("Samples");
  plt.legend(["True (-0.5 K)", "63-99 MHz linphys", "50-100 MHz linphys"]);
  plt.ylim([0, 450]);
  plt.savefig("{}_hist_recovered_amp_phys.png".format(outputBase));
  
  
#  plt.figure(6);
#  plt.clf();  
#  plt.hist(rcvSigPoly[1][2,0:648], bins=np.linspace(0,10, 6), density=False, histtype='stepfilled',facecolor='blue', linewidth=lw2, alpha=0.5); 
#  plt.hist(rcvSigPoly[0][2,0:648], bins=np.linspace(0,10, 6), density=False, histtype='stepfilled',facecolor='red', linewidth=lw2, alpha=0.75);
#  plt.plot([7, 7], [0, 500], 'k:');
#  plt.xlabel("Best fit amplitude [K]");
#  plt.ylabel("Samples");
#  plt.legend(["True (7)", "63-99 MHz poly", "50-100 MHz poly"]);
##  plt.ylim([0, 450]);
#  plt.savefig("{}_hist_recovered_tau_poly.png".format(outputBase));
  
  
  
  
  
# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();
