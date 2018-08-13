# -*- coding: utf-8 -*-
import numpy as np
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('..');
import analysis
import models
   
def main():

  # Parse command line arguments
  parser = argparse.ArgumentParser(description='Plots contents of ACQ file.');
  parser.add_argument('inputFile', help='Options for plotting contents of ACQ file.');
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
                      help='Reduce the number of spectra used in calculations and plots by the specified factor.');
  parser.add_argument('-r', '--raw',   
                      action='store_true', 
                      help='Plot the raw spectra for each switch position.');
  parser.add_argument('-c', '--corrected',   
                      action='store_true', 
                      help='Plot the individual 3-position switch corrected spectra overlaid on the same plot.');                      
  parser.add_argument('-i', '--integrate',   
                      action='store_true', 
                      help='Plot the integration (mean) of the 3-position corrected spectra.');                      
  parser.add_argument('-w', '--waterfall', 
                      action='store_true', 
                      help='Plot a waterfall of spectra.  Used with--corrected and/or --raw.');
  parser.add_argument('-f', '--fit',   
                      action='store_true',
                      help='Fit the integrated (mean) spectrum and plot the residuals.  Specify model details using --model and --nterms.');
  parser.add_argument('-m', '--model',   
                      nargs=1, default=['linpoly'],
                      help='Model to use if --fit is set.  Specify one of: linpoly, linphys, linlog');      
  parser.add_argument('-n', '--nterms',   
                      nargs=1, type=int, default=[5],
                      help='Number of terms to use in model fit.');                      
                     
  args = parser.parse_args();
  print(args);
  inputFile = args.inputFile;
  outputDir = args.output[0];
  start = args.start[0];
  stop = args.stop[0];
  fmin = args.fmin[0];
  fmax = args.fmax[0];
  thin = args.thin[0];
  model = args.model[0].lower();
  nterms = args.nterms[0];
  bPlotFit = args.fit;
  bPlotRaw = args.raw;
  bPlotCorrected = args.corrected;
  bPlotIntegration = args.integrate;
  bPlotWaterfall = args.waterfall;
  
  # Hard coded parameters -- should be added to commandline args at some point
  vc = 75;
  beta = -2.5;
  nkernel = 64;

  inputDir = os.path.dirname(inputFile);
  inputFilenameBase = os.path.splitext(os.path.basename(inputFile))[0];
  outputFullBase = outputDir + '/' + inputFilenameBase;

  # Read the input file
  spec, anc, freqs = analysis.readAcq(inputFile, start=start, stop=stop, verbose=1, seek=True);
  nspec = len(spec);
  nfreqs = len(freqs);
  channelSize = anc[0,10];

  p0 = spec[0:nspec:int(3*thin)];
  p1 = spec[1:nspec:int(3*thin)];
  p2 = spec[2:nspec:int(3*thin)];
  
  cor = analysis.correct(p0, p1, p2);
  
  freqssub = freqs[(freqs>=fmin) & (freqs<=fmax)];
  corsub = cor[:, (freqs>=fmin) & (freqs<=fmax)];

  # Integrate
  corsubmean = np.mean(corsub, axis=0);    

  # Fit with model and get residuals
  if model  == 'linpoly':
    components = models.linearPolynomialComponents(freqssub, vc, nterms, beta=beta);
  elif model == 'linphys':
    if nterms is not 5:
      print("Using 5 terms as requried by 'linphys' model.");
      nterms = 5;
    components = models.linearPhysicalComponents(freqssub, vc);
  elif model == 'linlog':
    components = models.linearLogExpansionComponents(freqssub, vc, nterms, beta=beta);
  else:
    print("Specified model '{}' was not recognized.  Using 'linpoly'.".format(model) );
    components = models.linearPolynomialComponents(freqssub, vc, nterms, beta=beta);
        
  fit, rms = models.fitLinear(corsubmean, components);
  print('RMS: {}'.format(rms));
  
  residuals = corsubmean - np.dot(components, fit);
  
  # Smooth residuals with boxcar kernel
  kernel = np.ones(nkernel) / nkernel;
  smoothres = np.convolve(residuals, kernel, 'same');
  smoothrms = np.std(smoothres);
  print('RMS smoothed ({}): {}'.format(nkernel, smoothrms));



  # Make the requested plots
  fig = 1;
  cmap = 'jet';
      
  
  if bPlotFit:
    
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    plt.plot(freqssub, residuals);
    plt.plot(freqssub, smoothres);
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("$T_{res}$ [K]");
    plt.xlim([fmin, fmax]);
    plt.legend(['{:.1f} kHz'.format(1e3*channelSize), '{:.1f} kHz (smoothed)'.format(1e3*nkernel*channelSize)]);
  
    ymax = np.max(residuals);
    ymin = np.min(residuals);
    if ymax>10000:
      ymax = np.median(residuals)*1.5;
    ydiff = ymax - ymin;
    ypad = ydiff * 0.1;  
  
    plt.ylim([ymin-ypad, ymax+ypad]);
    plt.savefig(outputFullBase + '_3pos_residuals_{}_nterms{}.png'.format(model, nterms));     
    
  if bPlotCorrected:
    
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    plt.plot(freqssub, corsub.transpose());
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("$T_{3pos}$ [K]");
    plt.xlim([fmin, fmax]);
    
    ymax = np.max(corsub[:]);
    ymin = np.min(corsub[:]);  
    if ymax>10000:
      ymax = np.median(corsub[:,0])*1.5;
    ydiff = ymax - ymin;
    ypad = ydiff * 0.1;  
    
    plt.ylim([ymin-ypad, ymax+ypad]);
    plt.savefig(outputFullBase + '_3pos.png');                   

    if bPlotIntegration:
      
      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.plot(freqssub, corsubmean);
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("$T_{3pos}$ [K]");
      plt.xlim([fmin, fmax]);
    
      ymax = np.max(corsubmean);
      ymin = np.min(corsubmean);
      if ymax>10000:
        ymax = np.median(corsub[:,0])*1.5;
      ydiff = ymax - ymin;
      ypad = ydiff * 0.1;  
    
      plt.ylim([ymin-ypad, ymax+ypad]);
      plt.savefig(outputFullBase + '_3pos_integration.png'); 
    
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

    if bPlotIntegration:
      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      h1, = plt.plot(freqs, np.mean(10*np.log10(p0), axis=0), 'b-', label='p0 (antenna)');
      h2, = plt.plot(freqs, np.mean(10*np.log10(p1), axis=0), 'g-', label='p1 (ambient)');
      h3, = plt.plot(freqs, np.mean(10*np.log10(p2), axis=0), 'r-', label='p2 (hot)');
                
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("p [dB]");  
      plt.ylim([-90, -50]);
      plt.legend(handles=[h1, h2, h3]);
      plt.savefig(outputFullBase + '_raw_integration.png');
      
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
      plt.savefig(outputFullBase + '_raw_waterfall_p0.png');                 

      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.imshow(10*np.log10(p1), extent=[freqs[0], freqs[len(freqs)-1], len(p0)*thin, 0], cmap=cmap, aspect='auto', origin='upper');
      plt.clim(clim);
      plt.colorbar(label='Arbitrary power [dB]');     
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("Spectrum # (p1)");
      plt.savefig(outputFullBase + '_raw_waterfall_p1.png');  
      
      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.imshow(10*np.log10(p2), extent=[freqs[0], freqs[len(freqs)-1], len(p0)*thin, 0], cmap=cmap, aspect='auto', origin='upper'); 
      plt.clim(clim);
      plt.colorbar(label='Arbitrary power [dB]');     
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("Spectrum # (p2)");   
      plt.savefig(outputFullBase + '_raw_waterfall_p2.png');  


    
           
        
        
        



# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();


