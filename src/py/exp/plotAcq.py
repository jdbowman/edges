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

  # Ignore divide by zero and related warnings caused by 3-position switch 
  # correction applied to full bandwidth (including <50 MHz)
  np.seterr(divide='ignore', invalid='ignore')
  
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
  parser.add_argument('-g', '--flag', 
                      action='store_true', 
                      help='Flag RFI in corrected integrations and residual plots.');                      
                     
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
  bFlagRFI = args.flag;
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

  nsize = nspec - (nspec % 3);
  p0 = spec[0:nsize:int(3*thin)];
  p1 = spec[1:nsize:int(3*thin)];
  p2 = spec[2:nsize:int(3*thin)];
  

  # Make the requested plots
  fig = 1;
  cmap = 'jet';
  lw = 0.75;  
  
  if bPlotRaw:
    
    print('Plotting raw spectra summary...');
    
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    
    plt.plot(freqs, np.max(10*np.log10(p0.transpose()), axis=1), color=[0.75,0.75,0.75], linewidth=lw);
    h0, = plt.plot(freqs, np.mean(10*np.log10(p0.transpose()), axis=1), 'k-', linewidth=lw, label='p0 (antenna)');
    plt.plot(freqs, np.min(10*np.log10(p0.transpose()), axis=1), color=[0.5,0.5,0.5], linewidth=lw);
   
    
    plt.plot(freqs, np.max(10*np.log10(p1.transpose()), axis=1), color=[0.75,0.75,1], linewidth=lw);
    h1, = plt.plot(freqs, np.mean(10*np.log10(p1.transpose()), axis=1), 'b-', linewidth=lw, label='p1 (antenna)');
    plt.plot(freqs, np.min(10*np.log10(p1.transpose()), axis=1), color=[0.5,0.5,1], linewidth=lw);
       
    plt.plot(freqs, np.max(10*np.log10(p2.transpose()), axis=1), color=[1,0.75,0.75], linewidth=lw);
    h2, = plt.plot(freqs, np.mean(10*np.log10(p2.transpose()), axis=1), 'r-', linewidth=lw, label='p2 (antenna)'); 
    plt.plot(freqs, np.min(10*np.log10(p2.transpose()), axis=1), color=[1,0.5,0.5], linewidth=lw);
    
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("p [dB]");  
    plt.ylim([-90, -50]);
    plt.legend(handles=[h0, h1, h2]);
    plt.savefig(outputFullBase + '_raw.png');
      
    if bPlotWaterfall:
      
      print('Plotting raw spectra waterfalls...');
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
         
      
      
  if bPlotCorrected or bPlotIntegration or bPlotFit:
        
    # Apply the 3-position correction
    print('Applying 3-position correction...');
    cor = analysis.correct(p0, p1, p2);
    
    # Reduce the frequency range to the specified bounds
    freqssub = freqs[(freqs>=fmin) & (freqs<=fmax)];
    corsub = cor[:, (freqs>=fmin) & (freqs<=fmax)];
    print('Frequency range reducted to {}-{} MHz ({} channels)'.format(fmin, fmax, corsub.shape[1]));

    # Integrate without filtering
    if bFlagRFI:
      
      # Integrate after flagging bad spectra
      rowWeights = analysis.flagAveragePower(corsub, threshold=1e4);
      corsubmean = np.sum((corsub.transpose()*rowWeights).transpose(), axis=0) / np.sum(rowWeights);
      
      flagComponents = models.linearPolynomialComponents(freqssub, vc=75, nterms=11, beta=0);
      channelWeights, flagrms = analysis.flagChannels(corsubmean, flagComponents, sigma=3, tol=0.0001, maxiter=20);
      
      print('Number of spectra flagged: {}'.format(corsub.shape[0] - np.sum(rowWeights)));      
      print('Number of channels flagged: {}'.format(corsub.shape[1] - np.sum(channelWeights)));
          
    else:
      
      corsubmean = np.mean(corsub, axis=0);  
      channelWeights = np.ones(corsubmean.shape);
        
     
  if bPlotCorrected:
    
    print('Plot 3-position corrected spectra summary...');
      
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    plt.plot(freqssub, np.max(corsub.transpose(), axis=1), 'r-', linewidth=lw);
    plt.plot(freqssub, np.min(corsub.transpose(), axis=1), 'b-', linewidth=lw);
    plt.plot(freqssub, np.mean(corsub.transpose(), axis=1), 'k-', linewidth=lw);   
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("$T_{3pos}$ [K]");
    plt.legend(['Max hold', 'Min hold', 'Mean']);
    plt.xlim([fmin, fmax]);
    
    ymax = np.nanmax(np.where(~np.isinf(corsub), corsub, np.nan));
    ymin = np.nanmin(np.where(~np.isinf(corsub), corsub, np.nan));  
    if ymax>10000:
      ymax = np.nanmedian(corsub[:,0])*1.5;
    ydiff = ymax - ymin;
    ypad = ydiff * 0.1;  
    
    plt.ylim([ymin-ypad, ymax+ypad]);
    plt.savefig(outputFullBase + '_3pos.png');                   
   
    if bPlotWaterfall:
      
      print('Plot 3-position corrected spectra waterfall...');
      
      plt.figure(fig);
      fig = fig + 1;
      plt.clf();
      plt.imshow(corsub, extent=[freqssub[0], freqssub[len(freqssub)-1], len(corsub)*thin, 0], cmap=cmap, aspect='auto', origin='upper');
      plt.clim([ymin, ymax]);
      plt.colorbar(label='$T_{3pos}$ [K]');     
      plt.xlabel("Frequency [MHz]");
      plt.ylabel("Spectrum #");
      plt.savefig(outputFullBase + '_3pos_waterfall.png');                   
      
      
  if bPlotIntegration:
  
    print('Plot 3-position corrected integrated spectrum...');

    ind = [i for i in range(len(channelWeights)) if channelWeights[i]==0];

    plotdata = corsubmean.copy();
    plotdata[ind] = np.nan;
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    plt.plot(freqssub, plotdata, linewidth=lw);
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("$T_{3pos}$ [K]");
    plt.xlim([fmin, fmax]);
  
    ymax = np.nanmax(np.where(~np.isinf(corsubmean), corsubmean, np.nan));
    ymin = np.nanmin(np.where(~np.isinf(corsubmean), corsubmean, np.nan));
    if ymax>10000:
      ymax = np.nanmedian(corsub[:,0])*1.5;
    ydiff = ymax - ymin;
    ypad = ydiff * 0.1;  
  
    plt.ylim([ymin-ypad, ymax+ypad]);
    plt.savefig(outputFullBase + '_3pos_integration.png');  
  

  if bPlotFit:

    print('Plot residuals to model fit...');
    
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
          
    # Do the fit
    ind = [i for i in range(len(channelWeights)) if ((channelWeights[i]==1) & (not np.isnan(corsubmean[i])))]; 
    fit, rms = models.fitLinear(corsubmean[ind], components[ind,:]);
    residuals = channelWeights * (corsubmean - np.dot(components, fit));
    rms = np.nanstd(residuals[ind]);
        
    # Smooth residuals with boxcar kernel
    kernel = np.ones(nkernel) / nkernel;
    smoothres = np.convolve(residuals, kernel, 'same');
    smoothrms = np.nanstd(smoothres);

    print('RMS: {:.4f} K'.format(rms));
    print('RMS smoothed ({:}): {:.4f} K'.format(nkernel, smoothrms));

    ind = [i for i in range(len(channelWeights)) if channelWeights[i]==0];     
    plotres = residuals.copy();
    plotres[ind] = float('NaN');
        
    plt.figure(fig);
    fig = fig + 1;
    plt.clf();
    plt.plot(freqssub, plotdata, 'b-', linewidth=lw);
    plt.plot(freqssub, smoothres, 'k-', linewidth=lw);
    plt.xlabel("Frequency [MHz]");
    plt.ylabel("$T_{res}$ [K]");
    plt.xlim([fmin, fmax]);
    plt.legend(['{:.1f} kHz'.format(1e3*channelSize), '{:.1f} kHz (smoothed)'.format(1e3*nkernel*channelSize)]);
  
    ymax = np.nanmax(np.where(~np.isinf(residuals), residuals, np.nan));
    ymin = np.nanmin(np.where(~np.isinf(residuals), residuals, np.nan));
    if ymax>10000:
      ymax = np.nanmedian(residuals)*1.5;
    ydiff = ymax - ymin;
    ypad = ydiff * 0.1;  
  
    plt.ylim([ymin-ypad, ymax+ypad]);
    plt.savefig(outputFullBase + '_3pos_residuals_{}_nterms{}.png'.format(model, nterms));     
    
    
           
        
        
        



# --------------------------------------------------------------------------- #
# Execute
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main();


