import numpy as np
import matplotlib.pyplot as plt
import argparse
import csv
import sys
sys.path.append('..');
import models

# --------------------------------------------------------------------------- #
# File helpers
# --------------------------------------------------------------------------- #
# Load a batch of simulated data files
def loadGroup(inputFileTemplate, modelSet, freqSet, noiseSet):

  spec = [[[[] for n in noiseSet] for f in freqSet] for m in modelSet];
  params = [[[[] for n in noiseSet] for f in freqSet] for m in modelSet];
  freqs = [[[[] for n in noiseSet] for f in freqSet] for m in modelSet];
  filenames = [[[[] for n in noiseSet] for f in freqSet] for m in modelSet];
  exists = [[[[] for n in noiseSet] for f in freqSet] for m in modelSet];
    
  # Read the files specified in the sets and populate an array with
  # pertinent content  
  for i,m in enumerate(modelSet):
    for j,f in enumerate(freqSet):
      for k,n in enumerate(noiseSet):
          
        filenames[i][j][k] = inputFileTemplate.format(f,m,n);
              
        try:
          spec[i][j][k], freqs[i][j][k], params[i][j][k], labels = models.readFile(filenames[i][j][k]);
          print("Added: " + filenames[i][j][k] );

          exists[i][j][k] = True;
        except:
          print("Does not exist: " + filenames[i][j][k]);
          exists[i][j][k] = False;
              
  return spec, params, freqs, filenames, exists;
  
  
# --------------------------------------------------------------------------- #
# Plotting helpers
# --------------------------------------------------------------------------- #  
def plotDualBandHistogram(freqs, params, p, bins, label=None, 
                          trueValue=None, fig=None):

  #bins = np.linspace(-2.05,2.05,42);
  lw = 1.5;
  
  if label is None:
    label = "Paramater {}".format(p);
  
  if fig is None:
    plt.figure();
  else:  
    plt.figure(fig);
    
  bv1 = plt.hist(params[1][p,:], bins=bins, density=False, 
                  histtype='stepfilled',facecolor='blue', linewidth=lw, alpha=0.5)[0]; 
  bv2 = plt.hist(params[0][p,:], bins=bins, density=False, 
                  histtype='stepfilled',facecolor='red', linewidth=lw, alpha=0.5)[0];
  maxbin = np.max([np.max(bv1), np.max(bv2)]);
  
  if trueValue is not None:
    plt.plot(trueValue*np.ones(2), [0, 1.1*maxbin], 'k:');
  
  legend = [];
  if trueValue is not None:
    legend.append("True ({0:6.3f})".format(trueValue));
  legend.append("{0:3.1f} - {1:3.1f} MHz".format(np.min(freqs[1]), np.max(freqs[1])));
  legend.append("{0:3.1f} - {1:3.1f} MHz".format(np.min(freqs[0]), np.max(freqs[0])));
  
  plt.legend(legend);
  plt.xlabel("{}".format(label));
  plt.ylabel("Samples");
  plt.ylim([0, 1.1*maxbin]);
          
          


  
            
# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():

  # Parse command line arguments
  parser = argparse.ArgumentParser(description='Fit simulated data.');
  parser.add_argument('infile', help='Options for plotting contents of CSV file.');
  parser.add_argument('-t', '--trials',   
                      action='store_true', 
                      help='Plot a parameter by trial number.');
  parser.add_argument('-s', '--spec',   
                      action='store_true', 
                      help='Plot the spectra in the file.');
  parser.add_argument('-i', '--hist', 
                      action='store_true', 
                      help='Plot histogram of parameter values.');
  parser.add_argument('-l', '--label', nargs=1,
                      help="Label to display on plot.");
  parser.add_argument('-p', '--param', nargs=1, type=int, default=[0],
                      help="The paramater to plot.");  
  parser.add_argument('-b', '--bins', nargs=3, type=float, default=[-1,1,100],
                      help="Bins for the histogram.  A list of there values that will be given to numpy.linspace");    
  parser.add_argument('-v', '--value', nargs=1, type=float,
                      help="True value to overlay on historgram");

                      
  args = parser.parse_args();
  print(args);
                      
  nsig = 4;
  p = args.param[0];
  bins = np.linspace(*args.bins);
  
  label = None if args.label is None else args.label[0];
  trueValue = None if args.value is None else args.value[0];
  bPlotHistogram = args.hist;
  bPlotTrials = args.trials;
  bPlotSpectra = args.spec;
  inputFile = args.infile;  
  
  if bPlotHistogram:
    print(bins)
       
  # Read the file specified 
  spec, freqs, params, labels = models.readFile(inputFile);

  # Get basic statistics of each parmater
  statsMedian = np.median(params, axis=1);
  statsMean = np.mean(params, axis=1);
  statsStd = np.std(params, axis=1);
  
  print("");
  print(inputFile)
  print("");
  print("Number of parameters: {}".format(params.shape[0]));
  print("");
  print("Medians: {}".format(", ".join(map("{:8.6f}".format, statsMedian))));
  print("Means: {}".format(", ".join(map("{:8.6f}".format, statsMean))));
  print("Std devs: {}".format(", ".join(map("{:8.6f}".format, statsStd))));
  print("");
  print("Number of frequency channels: {}".format(spec.shape[0]));
  print("");
  print("Number of spectra: {}".format(spec.shape[1]));
  print("");  
  
  # --------------------------------------------------------------------------- #
  # Plot the results
  # --------------------------------------------------------------------------- #
  
  lw = 1.5;
          
  if bPlotHistogram:
    
    print("Plotting histogram for parameter {}...".format(p));
    
    lw = 1.5;
    plt.figure(1); 
    plt.clf();           
    bv1 = plt.hist(params[p,:], bins=bins, density=False, 
                    histtype='stepfilled',facecolor='blue', linewidth=lw, alpha=0.5)[0]; 
                    
    maxbin = np.max(bv1);
    
    if trueValue is not None:
      plt.plot(trueValue*np.ones(2), [0, 1.1*maxbin], 'k:');

    if label is None:
      label = "Paramater {}".format(p);
      
    plt.xlabel("{}".format(label));
    plt.ylabel("Samples");
    plt.ylim([0, 1.1*maxbin]);           
    plt.savefig("{}_hist_p{}.png".format(inputFile[:-4], p));
                  
  if bPlotSpectra:
         
    print("Plotting spectra...");
           
    plt.figure(1);
    plt.clf();
    plt.plot(freqs, spec[:,0:-1:10]);
    plt.xlabel('Frequency [MHz]');
    plt.ylabel('T [K]');
    plt.xlim([50, 100]);
    plt.savefig("{}_spectra.png".format(inputFile[:-4])); 

  if bPlotTrials:
  
    print("Plotting trials for parameter {}...".format(p));
    
    if label is None:
      label = "Paramater {}".format(p);
      
    plt.figure(1);
    plt.clf();
    plt.plot(params[p,:], 'kx');  
    plt.xlabel('Trial #');
    plt.ylabel("{}".format(label));
    plt.savefig("{}_trials_p{}.png".format(inputFile[:-4], p));            
  
# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();
