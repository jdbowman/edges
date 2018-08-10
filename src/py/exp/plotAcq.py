# -*- coding: utf-8 -*-
import numpy as np
import argparse
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('..');
import analysis
   
def main():

  # Parse command line arguments
  parser = argparse.ArgumentParser(description='Plots contents of ACQ file.');
  #parser.add_argument('inputFile', help='Options for plotting contents of ACQ file.');
  parser.add_argument('-o', '--output',   
                      nargs=1, default=['.'],
                      help='Output directory.');
  parser.add_argument('-b', '--start',   
                      nargs=1, type=int, default=[0],
                      help='Start reading on specified line in the file (first line is 0).  Negative values count back from end of file.  There are two lines per spectrum and six lines per switch cycle.');
  parser.add_argument('-e', '--stop',   
                      nargs=1, type=int, default=[9999999],
                      help='Stop reading before specified line in the file.  Negative values count back from end of file.  There are two lines per spectrum and six lines per switch cycle.');                      
  parser.add_argument('-l', '--fmin',   
                      nargs=1, type=float, default=[50],
                      help='Minimum frequency to plot.');
  parser.add_argument('-u', '--fmax',   
                      nargs=1, type=float, default=[199],
                      help='Maximum frequency to plot.');  
  parser.add_argument('-t', '--thin',   
                      nargs=1, type=int, default=[1],
                      help='Reduce the number of plotted spectra by the specified amount.');
  parser.add_argument('-r', '--raw',   
                      action='store_true', 
                      help='Plot the raw spectra for each switch position.');
  parser.add_argument('-c', '--corrected',   
                      action='store_true', 
                      help='Plot the 3-position switch corrected spectra.');                      
  parser.add_argument('-m', '--mean',   
                      action='store_true', 
                      help='Plot the mean of the spectra.');                      
  parser.add_argument('-w', '--waterfall', 
                      action='store_true', 
                      help='Plot a waterfall of the spectra.');
                     
  args = parser.parse_args();
  print(args);
               
  outputDir = args.output[0];
  start = args.start[0];
  stop = args.stop[0];
  fmin = args.fmin[0];
  fmax = args.fmax[0];
  thin = args.thin[0];
  bPlotRaw = args.raw;
  bPlotCorrected = args.corrected;
  bPlotMean = args.mean;
  bPlotWaterfall = args.waterfall;

  inputFile = 'C:/Users/jdbowman/Downloads/2018_221_low2.acq ';
  outputDir = 'C:/Users/jdbowman/Downloads';
  bPlotRaw = True;
  bPlotCorrected = True;
  bPlotMean = False;
  bPlotWaterfall = True;
  thin = 1;
  start = -18
  
  inputDir = os.path.dirname(inputFile);
  inputFilenameBase = os.path.splitext(os.path.basename(inputFile))[0];
  outputFullBase = outputDir + '/' + inputFilenameBase;

  # Read the input file
  spec, anc, freqs = analysis.readAcq(inputFile, start=start, stop=stop, verbose=1, seek=True);
  nspec = len(spec);
  nfreqs = len(freqs);

  p0 = spec[0:nspec:int(3*thin)];
  p1 = spec[1:nspec:int(3*thin)];
  p2 = spec[2:nspec:int(3*thin)];
  
  cor = analysis.correct(p0, p1, p2);

  freqssub = freqs[(freqs>=fmin) & (freqs<=fmax)];
  corsub = cor[:, (freqs>=fmin) & (freqs<=fmax)];
  corsubmean = np.mean(corsub, axis=0);    

  # Make the requested plots
  fig = 1;
  cmap = 'jet';
  
  if bPlotCorrected:
    
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    if bPlotMean:
      ymax = np.max(corsubmean);
      ymin = np.min(corsubmean);
      plt.plot(freqssub, corsubmean);
      suffix = '_3pos_mean.png';
    else:
      plt.plot(freqssub, corsub.transpose());
      ymax = np.max(corsub[:]);
      ymin = np.min(corsub[:]);
      suffix = '_3pos.png';
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("$T_{3pos}$ [K]");
    plt.xlim([fmin, fmax]);
  
    if ymax>10000:
      ymax = np.median(corsub[:,0])*1.5;

    ydiff = ymax - ymin;
    ypad = ydiff * 0.1;  
    plt.ylim([ymin-ypad, ymax+ypad]);
    plt.savefig(outputFullBase + suffix);                   

    if bPlotWaterfall:
      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.imshow(corsub, extent=[freqssub[0], freqssub[len(freqssub)-1], len(corsub)*thin, 0], cmap=cmap, aspect='auto', origin='upper');
      plt.clim([ymin, ymax]);
      plt.colorbar(label='$T_{3pos}$ [K]');     
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("Spectrum #");
      plt.savefig(outputFullBase + '_3pos_waterfall.png');                   
      
  
  if bPlotRaw:
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    if bPlotMean:
      h1, = plt.plot(freqs, np.mean(10*np.log10(p0), axis=0), 'b-', label='p0 (antenna)');
      h2, = plt.plot(freqs, np.mean(10*np.log10(p1), axis=0), 'g-', label='p1 (ambient)');
      h3, = plt.plot(freqs, np.mean(10*np.log10(p2), axis=0), 'r-', label='p2 (hot)');
    else:
      plt.plot(freqs, 10*np.log10(p0.transpose()), 'b-');
      plt.plot(freqs, 10*np.log10(p1.transpose()), 'g-');
      plt.plot(freqs, 10*np.log10(p2.transpose()), 'r-');
      
      h1, = plt.plot(freqs, 10*np.log10(p0[0].transpose()), 'b-', label='p0 (antenna)');
      h2, = plt.plot(freqs, 10*np.log10(p1[0].transpose()), 'g-', label='p1 (ambient)');
      h3, = plt.plot(freqs, 10*np.log10(p2[0].transpose()), 'r-', label='p2 (hot)');
      
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("p [dB]");  
    plt.ylim([-90, -50]);
    plt.legend(handles=[h1, h2, h3]);
    plt.savefig(outputFullBase + '_raw.png');
    
    if bPlotWaterfall:
      
      clim = [-90, -75];
      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.imshow(10*np.log10(p0), extent=[freqs[0], freqs[len(freqs)-1], len(p0)*thin, 0], cmap=cmap, aspect='auto', origin='upper');
      plt.clim(clim);
      plt.colorbar(label='Arbitrary power [dB]');     
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("Spectrum # (p0)");
      plt.savefig(outputFullBase + '_raw_p0_waterfall.png');                 

      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.imshow(10*np.log10(p1), extent=[freqs[0], freqs[len(freqs)-1], len(p0)*thin, 0], cmap=cmap, aspect='auto', origin='upper');
      plt.clim(clim);
      plt.colorbar(label='Arbitrary power [dB]');     
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("Spectrum # (p1)");
      plt.savefig(outputFullBase + '_raw_p1_waterfall.png');  
      
      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.imshow(10*np.log10(p2), extent=[freqs[0], freqs[len(freqs)-1], len(p0)*thin, 0], cmap=cmap, aspect='auto', origin='upper'); 
      plt.clim(clim);
      plt.colorbar(label='Arbitrary power [dB]');     
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("Spectrum # (p2)");   
      plt.savefig(outputFullBase + '_raw_p2_waterfall.png');  


    
           
        
        
        



# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();


