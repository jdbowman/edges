import numpy as np
import argparse
import csv
import sys
import time
sys.path.append('..');
import models


  
# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():

  # Parse command line arguments
  parser = argparse.ArgumentParser(description='Fit simulated data.');
  parser.add_argument('infile', help='Input file containing foreground simulations');
  parser.add_argument('-m', '--model', nargs=1, default=['linpoly'], 
                      help='linpoly, linphys, or linlog');
  parser.add_argument('-s', '--addsig',   
                      action='store_true', 
                      help='Adds a simulated signal to every foreground realization.');
  parser.add_argument('-n', '--addnoise', 
                      action='store_true', 
                      help='Adds simulated thermal noise to every foreground realization.');
  parser.add_argument('-g', '--grid',  
                      action='store_true',
                      help="Perform grid search for a signal in each simulation.");
  parser.add_argument('-f', '--fit', 
                      action='store_true',
                      help="Fit a linear model to each simulation.");
  parser.add_argument('-c', '--cov', action='store_true',
                      help="Use an estimated covariance matrix in the grid search.  ONLY used in grid search.  Currently this is placeholder diagonal matrix based on thermal noise.");
  parser.add_argument('-t', '--nterms', nargs=1, type=int,
                      default=[5]);
  parser.add_argument('-b', '--beta', nargs=1, type=int,
                      default=[-2.5]);                      
  parser.add_argument('-r', '--thermal', nargs=1, type=float, 
                      default=[0.025], 
                      help='Specify the thermal noise per frequency bin in Kelvin');
  parser.add_argument('-o', '--output', nargs=1, 
                      default='./', 
                      help='Path to directory for output files.');
  
  args = parser.parse_args()
  print(args)
  
  outputDir = args.output[0];     #'/home/loco/analysis/';
  inputFile = args.infile;        #'/home/loco/analysis/foreground_mini_simulations_freq0.csv';
  bIncludeSignal = args.addsig;   #False;
  bIncludeNoise = args.addnoise;  #False;
  bDoGridSearch = args.grid;      #False;
  bDoForegroundOnlyFit = args.fit;#False;
  bUseCov = args.cov;
  model = args.model[0];          #'linpoly';
  thermalNoise = args.thermal[0];    #0.025;
  beta = args.beta[0];               #-2.5;
  nterms = args.nterms[0];           #5;
  vc = 75.0;
  nInputParams = 7;
  signalFunction = models.flattenedGaussian;
  signalArgs = [80, 20, 7, -0.5];
  
  
  # --------------------------------------------------------------------------- #
  # Read in the input foreground simulation file 
  # --------------------------------------------------------------------------- #
  nrows = models.numRows(inputFile);
  set, freqs, params, paramLabels = models.readFile(inputFile);               
  nfreqs = len(freqs);
       
  # --------------------------------------------------------------------------- #
  # Add any requested additions
  # --------------------------------------------------------------------------- #      
  if bIncludeSignal is True: 
    set = (set.transpose() + signalFunction(freqs, signalArgs).transpose()).transpose();
    
  if bIncludeNoise is True:
    set = set + thermalNoise * np.random.standard_normal(size=set.shape);
 
  # --------------------------------------------------------------------------- #
  # Generate the foreground components of the models we'll fit
  # --------------------------------------------------------------------------- #    
  if model == 'linpoly':
    foregroundComponents = models.linearPolynomialComponents(freqs, vc, nterms, beta=beta);
  elif model == 'linphys':
    foregroundComponents = models.linearPhysicalComponents(freqs, vc);
  elif model == 'linlog':
    foregroundComponents = models.linearLogExpansionComponents(freqs, vc, nterms, beta=beta);
  else:
    print("Failed.  Can't find model: {}".format(model));
    return;
  
  # --------------------------------------------------------------------------- #
  # Fit the simulated foregrounds 
  # --------------------------------------------------------------------------- #
  if bDoForegroundOnlyFit is True:
  
    fits = [models.fitLinear(set[:,x], foregroundComponents) for x in range(set.shape[1])];
    
    fo_recovParams = np.array([x[0] for x in fits]).transpose();
    fo_recovRMS = np.array([x[1] for x in fits]);
    fo_recovResiduals = set - foregroundComponents.dot(fo_recovParams);
    
    # Write results to file
    filename = "{}_fits_{}_sig{}_noise{}.csv".format(inputFile[:-4], model, bIncludeSignal, bIncludeNoise);
    with open(filename, "w") as csvFile:
      csvWriter = csv.writer(csvFile);
       
      # Write header
      csvWriter.writerow(["f{}".format(n) for n in range(nterms)] + ["RMS [K]"] + ["{0:8.6f}".format(n) for n in freqs]);

      # Write data
      for j in range(set.shape[1]):
        csvWriter.writerow(np.concatenate( (np.array(fo_recovParams[:,j]), fo_recovRMS[j], fo_recovResiduals[:,j])) );
        
          
  # --------------------------------------------------------------------------- #
  # Do grid search for signal
  # --------------------------------------------------------------------------- #
  if bDoGridSearch is True:
  
    # Generate the signal grid for searching (20500 points)
    steps_sig = [
      np.linspace(55, 100, 10), 
      np.linspace(5, 50, 10),
      np.linspace(1, 9, 5),
      np.linspace(-2, 2, 41)];
      
    steps_sig = [
      np.linspace(60, 90, 31), 
      np.linspace(1, 40, 40),
      np.linspace(1, 10, 10),
      np.linspace(-2, 2, 81)];      
      
    # Generate all parmeter grid points
    params_sig = models.populateGrid(steps_sig);
    
    # Generate realizations of the signal at each parameter grid point    
    realizations_sig = np.array([models.flattenedGaussian(freqs, p) for p in params_sig.transpose()]).transpose();
    
    # Generate noise covariance matrix
    if bUseCov:
      noiseCov = np.diag(thermalNoise**2 * np.ones([nfreqs]));
    else:
      noiseCov = None;  
        
    # Allocate output arrays
    gs_recovParams = np.zeros([nterms, set.shape[1]]);
    gs_recovSig = np.zeros([params_sig.shape[0], set.shape[1]]);
    gs_recovRMS = np.zeros(set.shape[1]); 
    gs_recovResiduals = np.zeros([nfreqs, set.shape[1]]); 

    # Write results to file on the fly
    filename = "{}_gridsearch{}_{}_sig{}_noise{}_cov{}.csv".format(inputFile[:-4], 
               params_sig.shape[1], model, bIncludeSignal, bIncludeNoise, bUseCov);
               
    with open(filename, "w") as csvFile:
      csvWriter = csv.writer(csvFile);
       
      # Write header
      csvWriter.writerow(["f{}".format(n) for n in range(nterms)] +
                        ["s{}".format(n) for n in range(params_sig.shape[0])] + 
                        ["RMS [K]"] + ["{0:8.6f}".format(n) for n in freqs]); 
                                
      # Loop over all simulated spectra and perform the grid search on each
      tic = time.time();
      for i in range(set.shape[1]):
      
        #fits, rmss = models.searchSignalTrials(set[:,i], foregroundComponents, 
        #                                 freqs, signalFunction, params_sig, dataCov=noiseCov);

        fits, rmss = models.searchSignalRealizations(set[:,i], foregroundComponents, 
                                         freqs, realizations_sig, dataCov=noiseCov);
                                         
        index = np.argmin(rmss);
        gs_recovParams[:,i] = fits[:,index];
        gs_recovSig[:,i] = params_sig[:,index];
        gs_recovRMS[i] = rmss[index]; 
        gs_recovResiduals[:,i] = set[:,i] - foregroundComponents.dot(gs_recovParams[:,i]) - signalFunction(freqs, gs_recovSig[:,i]); 
        #gs_recovResiduals[:,i] = set[:,i] - foregroundComponents.dot(gs_recovParams[:,i]) - realizations_sig[:,i]; 
                                
        # Write row                                 
        csvWriter.writerow( list(gs_recovParams[:,i]) + list(gs_recovSig[:,i]) + [gs_recovRMS[i]] + list(gs_recovResiduals[:,i]) );
    
        # Print update to stdout
        print("{0:8.2f} s ({1} of {2}): RMS {3:6.3} K -- {4:6.3f}, {5:6.3f}, {6:6.3f}, {7:6.3f}".format(time.time() - tic, i, set.shape[1], gs_recovRMS[i], gs_recovSig[0,i], gs_recovSig[1,i], gs_recovSig[2,i], gs_recovSig[3,i]));
    
    
  
     
  
# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();
