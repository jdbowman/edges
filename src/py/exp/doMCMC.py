import numpy as np
import argparse
import csv
import sys
import time
from datetime import datetime
sys.path.append('..');
import models
import emcee


  
# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():

  # Parse command line arguments
  parser = argparse.ArgumentParser(description='Perform an MCMC parameter estimation on a spectrum.');
  parser.add_argument('infile', help='Input file containing foreground simulations or data');
  parser.add_argument('-m', '--model', nargs=1, default=['linpoly'], 
                      help='linpoly, linphys, linlog, or explog');
  parser.add_argument('-s', '--addsig',   
                      action='store_true', 
                      help='Adds a simulated signal to every foreground realization.');
  parser.add_argument('-n', '--addnoise', 
                      action='store_true', 
                      help='Adds simulated thermal noise to every foreground realization.');
  parser.add_argument('-i', '--index', nargs=1, type=int,
                      default=None,
                      help='Row index of the spectrum to use if the input file is a simulation file.');
  parser.add_argument('-t', '--nterms', nargs=1, type=int,
                      default=[5]);
  parser.add_argument('-b', '--beta', nargs=1, type=int,
                      default=[-2.5]);                     
  parser.add_argument('-l', '--fmin', nargs=1, type=float,
                      default=[50]); 
  parser.add_argument('-u', '--fmax', nargs=1, type=float,
                      default=[100]);                                                                  
  parser.add_argument('-e', '--niter', nargs=1, type=int,
                      default=[25000]);   
  parser.add_argument('-w', '--nwalker', nargs=1, type=int,
                      default=[200]);   
  parser.add_argument('-p', '--ntemp', nargs=1, type=int,
                      default=[8]);                       
  parser.add_argument('-r', '--thermal', nargs=1, type=float, 
                      default=[0.025], 
                      help='Specify the thermal noise per frequency bin in Kelvin');
  parser.add_argument('-a', '--args', nargs='*', type=float, default=[80, 20, 7, -0.5],
                      help="Arguments to the signal function if --addsignal is used.");   
  
  args = parser.parse_args()
  print(args)
  
  #outputDir = args.output[0];     #'/home/loco/analysis/';
  inputFile = args.infile;        #'/home/loco/analysis/foreground_mini_simulations_freq0.csv';
  bIncludeSignal = args.addsig;   #False;
  bIncludeNoise = args.addnoise;  #False;
  model = args.model[0];          #'linpoly';
  thermalNoise = args.thermal[0];    #0.025;
  beta = args.beta[0];               #-2.5;
  nterms = args.nterms[0];           #5;
  vc = 75.0;
  fmin = args.fmin[0];
  fmax = args.fmax[0];
  simIndex = None if args.index is None else args.index[0];  
  signalArgs = args.args;         #[80, 20, 7, -0.5];
  signalFunction = models.flattenedGaussian;
  niters = args.niter[0];
  nwalkers = args.nwalker[0];
  ntemps = args.ntemp[0];
  nthreads = 12;
    
  # --------------------------------------------------------------------------- #
  # Read in the input foreground simulation file or data file
  # --------------------------------------------------------------------------- #
  if simIndex is not None:
  
    # The input file is a simulation
    data, v, params, paramLabels = models.readFile(inputFile);               
    d = data[:,index];
    w = np.ones_like(d);
    
  else: 
  
    # The input file is a data file
    data = np.genfromtxt(inputFile, delimiter=',', skip_header=1);
    v = data[:,0];
    w = data[:,1];
    d = data[:,2];
  
  # Select the channels to use
  spec = np.array(d[(v>=fmin) & (v<=fmax) & (w>0)]);
  freqs = np.array(v[(v>=fmin) & (v<=fmax) & (w>0)]);  
  nfreqs = len(freqs);
  
  # Make the uncertainty vector [[To do: this should really be different parameter than the addnoise below]]
  err = thermalNoise * np.ones_like(spec);

  # --------------------------------------------------------------------------- #
  # Add any requested additions
  # --------------------------------------------------------------------------- #      
  if bIncludeSignal is True: 
    spec = spec + signalFunction(freqs, signalArgs);
    
  if bIncludeNoise is True:
    spec = spec + thermalNoise * np.random.standard_normal(size=spec.shape);
 

  # --------------------------------------------------------------------------- #
  # Setup and run the MCMC
  # --------------------------------------------------------------------------- #   

  # Setup the foreground model
  if model == 'linpoly':
    likeFunc = models.probLinearPolynomial_FlattenedGaussian;
    likeArgs = (freqs, spec, err, vc, beta);
    labels = ["a0", "a1", "a2", "a3", "a4", "v0", "w", "tau", "A"];
    guess_mean = [1500, 1, 1, 1, 1,            65, 10, 1, 0];
    guess_sigma = [500, 500, 500, 500, 500,    10, 10, 1, 1]; 
       
  elif model == 'linphys':
    likeFunc = models.probLinearPhysical_FlattenedGaussian;
    likeArgs = (freqs, spec, err, vc);
    labels = ["a0", "a1", "a2", "a3", "a4", "v0", "w", "tau", "A"];
    guess_mean = [1500, 1, 1, 1, 1,            65, 10, 1, 0];
    guess_sigma = [500, 500, 500, 500, 500,    10, 10, 1, 1];  
        
  elif model == 'linlog':
    likeFunc = models.probLinearLogExpansion_FlattenedGaussian;
    likeArgs = (freqs, spec, err, vc, beta);
    labels = ["a0", "a1", "a2", "a3", "a4", "v0", "w", "tau", "A"];
    guess_mean = [1500, 1, 1, 1, 1,            65, 10, 1, 0];
    guess_sigma = [500, 500, 500, 500, 500,    10, 10, 1, 1]; 
         
  elif model == 'explog':
    likeFunc = models.probExponentLogExpansion_FlattenedGaussian;
    likeArgs = (freqs, spec, err, vc);
    labels = ["a0", "a1", "a2", "a3", "a4", "v0", "w", "tau", "A"];
    guess_mean = [1500, -2.5, 0, 0, 0,         65, 10, 1, 0];
    guess_sigma = [500, 2, 1, 1, 1,            10, 10, 1, 1];  
  else:
    print("Failed.  Can't find model: {}".format(model));
    return;
    
  # Setup the priors   
  priorFunc = models.logUniformPriors;
  priors = [[-1e5, 1e5], [-1e5, 1e5], [-1e5, 1e5], [-1e5, 1e5], [-1e5, 1e5], 
            [50, 100], [1, 100], [0.01, 100], [-1e5, 1e5]];
  
  # Setup the sampler
  ndim = np.size(guess_mean);

  # Create the starting positions for each walker
  pos = [models.populateRandom(guess_mean, guess_sigma, priors, nwalkers) for i in range(ntemps)];
                  
  # Use the parallel tempered sampler for multi-modal systems  
  sampler = emcee.PTSampler(ntemps,
                            nwalkers, 
                            ndim, 
                            likeFunc,
                            priorFunc,
                            loglargs=likeArgs,
                            logpargs=[priors],
                            loglkwargs={'priors':None},
                            threads=nthreads);

  # Run the sampler
  tic = time.time();  
  sampler.run_mcmc(pos, niters);
  duration = time.time() -tic;

  # --------------------------------------------------------------------------- #
  # Save the sample chains and configuration
  # --------------------------------------------------------------------------- # 
  
  # Get the current time for file timestamps
  currentTime = datetime.now();
  base = "{}_mcmc_{}_{}".format(inputFile[:-4], model, "{:%Y_%m_%dT%H_%M}".format(currentTime));
  
  # Save samples from each temperature to a separate file 
  for t in range(ntemps):
    samples = sampler.chain[t,:,:,:].reshape((-1, ndim));
    hdr = ", ".join([str(a) for a in labels]);
    np.savetxt(base + "_temp{:02}.csv".format(t), samples, delimiter=",", header=hdr);
  
  # Save the config to file
  with open(base + ".cfg", "w") as f:
    print("sampler = EMCEE Parallel Tempered Sampler", file=f);
    print("runTime: {}".format(duration), file=f);
    print("nDim = {}".format(ndim), file=f);
    print("nTemps = {}".format(ntemps), file=f);
    print("nWalkers = {}".format(nwalkers), file=f);
    print("nIterations = {}".format(niters), file=f);
    print("fMin = {}".format(fmin), file=f);
    print("fMax = {}".format(fmax), file=f);
    print("thermalNoise = {}".format(thermalNoise), file=f);
    print("commandLineArgs = {}".format(args), file=f);
    print("parameterLabels = {}".format(labels), file=f);
    print("spec = {}".format(spec), file=f);
    print("freqs = {}".format(freqs), file=f);
    print("err = {}".format(err), file=f);
    print("startPositions = {}".format(pos), file=f);
    print("seedMeans = {}".format(guess_mean), file=f);
    print("seedSigmas = {}".format(guess_sigma), file=f);
    print("priors = {}".format(priors), file=f);
    
    
  
     
  
# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();
