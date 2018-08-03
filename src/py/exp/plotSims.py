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
  parser.add_argument('infiletemplate', help='Options for plotting contents of CSV file.');
  parser.add_argument('-t', '--trials',   
                      action='store_true', 
                      help='Plot a parameter by trial number.');
  parser.add_argument('-s', '--spec',   
                      action='store_true', 
                      help='Plot the spectra in the file.');
  parser.add_argument('-i', '--hist', 
                      action='store_true', 
                      help='Plot histogram of parameter values.');
  parser.add_argument('-d', '--dualhist',  
                      action='store_true',
                      help="Plot dual histogram of parameter values by frequency range.");
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
  bPlotDualHistogram = args.dualhist;
  bPlotTrials = args.trials;
  bPlotSpectra = args.spec;
  inputFileTemplate = args.infiletemplate;  #'foreground_mini_simulation_freq{}_gridsearch20500_{}_sigTrue_noise{}.csv';
  
  print(bins)
  #bins = np.linspace(-2.05,2.05,42);
  #bins = np.linspace(-0.015,0.075,52);
  
  modelSet = ['linpoly', 'linphys', 'linlog'];
  freqSet = [0, 1];
  noiseSet = [True, False];

      
  # Read the files specified in the sets and populate an array with
  spec, params, freqs, filenames, exists = loadGroup(inputFileTemplate, modelSet, freqSet, noiseSet);

  
  # --------------------------------------------------------------------------- #
  # Plot the results
  # --------------------------------------------------------------------------- #
  
  lw = 1.5;
  
  for i, m in enumerate(modelSet):
    for j, f in enumerate(freqSet):
      for k, n in enumerate(noiseSet):
      
        if exists[i][j][k]:
        
          if bPlotDualHistogram:
          
            if exists[i][0][k] and exists[i][1][k]:
                            
              print("Plotting dual band histogram for parameter {}...".format(p));
              
              plotDualBandHistogram(
                [freqs[i][a][k] for a,b in enumerate(freqSet)], 
                [params[i][a][k] for a,b in enumerate(freqSet)],
                p, bins, label=label, trueValue=trueValue);    
                     
              plt.savefig("{}_dualhist_p{}.png".format(filenames[i][j][k][:-4], p));
     
          if bPlotHistogram:
            
            print("Plotting histogram for parameter {}...".format(p));
            
            lw = 1.5;
            plt.figure(1); 
            plt.clf();           
            bv1 = plt.hist(params[i][j][k][p,:], bins=bins, density=False, 
                            histtype='stepfilled',facecolor='blue', linewidth=lw, alpha=0.5)[0]; 
                            
            maxbin = np.max(bv1);
            
            if trueValue is not None:
              plt.plot(trueValue*np.ones(2), [0, 1.1*maxbin], 'k:');

            if label is None:
              label = "Paramater {}".format(p);
              
            plt.xlabel("{}".format(label));
            plt.ylabel("Samples");
            plt.ylim([0, 1.1*maxbin]);           
            plt.savefig("{}_hist_p{}.png".format(filenames[i][j][k][:-4], p));
                          
          if bPlotSpectra:
                 
            print("Plotting spectra...");
                   
            plt.figure(1);
            plt.clf();
            plt.plot(freqs[i][j][k], spec[i][j][k][:,0:-1:10]);
            plt.xlabel('Frequency [MHz]');
            plt.ylabel('T [K]');
            plt.xlim([50, 100]);
            #plt.ylim(0.1*np.max(spec[i][j][k][:])*np.array([-1, 1]));
            plt.savefig("{}_spectra.png".format(filenames[i][j][k][:-4])); 

          if bPlotTrials:
          
            print("Plotting trials for parameter {}...".format(p));
            
            if label is None:
              label = "Paramater {}".format(p);
              
            plt.figure(1);
            plt.clf();
            plt.plot(params[i][j][k][p,:], 'kx');  
            plt.xlabel('Trial #');
            plt.ylabel("{}".format(label));
            plt.savefig("{}_trials_p{}.png".format(filenames[i][j][k][:-4], p));            
  
# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();
