import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys
import time
from datetime import datetime
sys.path.append('..');
import models
import corner

  
# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():

  # Parse command line arguments
  parser = argparse.ArgumentParser(description='Plots results of an MCMC parameter estimation.');
  parser.add_argument('infile', help='Input file containing samples from an MCMC run.');
  parser.add_argument('-a', '--chains', action='store_true', 
                      help="Plot the chains for each parameter.");  
  parser.add_argument('-c', '--corner', action='store_true', 
                      help="Plot the corner graph.");                                                                                         
  parser.add_argument('-e', '--niter', nargs=1, type=int,
                      default=[25000]); 
  parser.add_argument('-n', '--nburn', nargs=1, type=int,
                      default=[20000]); 
  
  args = parser.parse_args()
  print(args)
  
  inputFile = args.infile;
  niters = args.niter[0];
  nburn = args.nburn[0];
  bPlotChains = args.chains;
  bPlotCorner = args.corner;

  # Read the input file of samples
  print("Reading: {}".format(inputFile));
  samples = np.genfromtxt(inputFile, delimiter=',', skip_header=1)
 
  nparams = samples.shape[1];
  nwalkers = int(samples.shape[0] / niters);

  # Reshape the loaded 2D data into 3D (walkers x iterations x params)
  samples = np.reshape(samples, [nwalkers, niters, nparams]);
  print(samples.shape)
  
  # Plot the chains
  if bPlotChains:   
    print("Plotting chains.");
    for i in range(nparams):
      plt.figure(i);
      plt.clf();
      plt.plot(samples[:,0:-1:10,i].transpose(), 'k-', linewidth=0.1);
      plt.savefig("{}_chains_p{}.png".format(inputFile[:-4], i));


  # Reduce to the only the samples post burn-in and flatten over walkers and iterations
  samples = samples[:,nburn:,:].reshape((-1, nparams));
  
  # Get the best fits and confidence ranges (68%, 95%, 99%)
  levels = [0.5, 2.5, 16, 50, 84, 97.5, 99.5];
  index = int(len(levels)/2);
  percentiles = np.percentile(samples, levels, axis=0);
  bounds = percentiles - percentiles[index];
  
  # Plot corner graph
  if bPlotCorner:
    print("Plotting corner graph.");
    corner.corner(samples, labels=["$a0$", "$a1$", "$a2$", "a3", "a4", "v0", "w", "tau", "A"]);
    plt.savefig("{}_corner.png".format(inputFile[:-4]));

  # Write statistics to file
  with open("{}_results.txt".format(inputFile), "w") as text_file:
   
    print("Percentiles: {}".format(levels));
    print("Percentiles: {}".format(levels), file=text_file);
    
    for i in range(nparams):
           
      print("Param {} best fit: {}".format(i, percentiles[index][i]));     
      print("Param {} best fit: {}".format(i, percentiles[index][i]), file=text_file);  
      print("Param {} confidence bounds: {}".format(i, ["{:8.6f}".format(a) for a in bounds.transpose()[i]]));
      print("Param {} confidence bounds: {}".format(i, ["{:8.6f}".format(a) for a in bounds.transpose()[i]]), file=text_file);



# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();
