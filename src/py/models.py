"""
Name: models.py
Desc: Collection of models for simulating EDGES data and analysis
"""

import numpy as np
import time
import csv

# --------------------------------------------------------------------------- #
# Signal and instrumental models
# --------------------------------------------------------------------------- #

# 21cm phenomenological signal model used in Bowman et al. 2018
# theta = [v0, w, tau, A]
def flattenedGaussian(v, theta):
    B = 4 * (v - theta[0])**2 * theta[1]**(-2) * np.log( -np.log( (1+np.exp(-theta[2]))/2) / theta[2]);
    return theta[3] * ( (1 - np.exp(-theta[2] * np.exp(B))) / (1 - np.exp(-theta[2])) );
      
# Simple sinusoidal model   
# theta = [period, phi, A]
def sinusoid(v, theta):
   return theta[2] * np.sin(2*np.pi*v/theta[0] + theta[1]);
 

# --------------------------------------------------------------------------- #
# Linear / linearized foreground models
# --------------------------------------------------------------------------- #

# An abstracted polynomial model that allows the exponent to be offset by beta.
# Note: A unity vector is not necessarily included in the model, depending on 
# the value of beta.
def linearPolynomialComponents(v, vc, nterms, beta=-2.5):
  normFreqs = v/vc;
  out = np.empty([v.size, nterms], dtype=float);
  for i in range(0, nterms):
    out[:,i] = normFreqs**(beta+i);    
  return out; 
    
def linearPolynomial(v, vc, terms, beta=-2.5):
  components = linearPolynomialComponents(v, vc, terms.size, beta);
  return components.dot(terms);
    

# The linearized version of a two-term exponential power-law foreground and  
# ionosphere contribuions.  Used in Bowman et al. 2018 as the linearized 
# physically-motivated model.
def linearPhysicalComponents(v, vc):
  normFreqs = v/vc;
  logFreqs = np.log10(v/vc);  
  out = np.empty([v.size, 5], dtype=float);
  out[:,0] = np.power(normFreqs, -2.5);
  out[:,1] = np.power(normFreqs, -2.5) * logFreqs;
  out[:,2] = np.power(normFreqs, -2.5) * logFreqs**2;
  out[:,3] = np.power(normFreqs, -4.5);
  out[:,4] = np.power(normFreqs, -2.0);  
  return out;
    
def linearPhysical(v, vc, terms):
  components = linearPhysicalComponents(v, vc);
  return components.dot(terms);


# A linear power-law expansion using powers of log10(frequency) after a 
# a fiducial spectral index, beta. Note: Also called the quasi-physical model.
def linearLogExpansionComponents(v, vc, nterms, beta=-2.5):
  logFreqs = np.log10(v/vc);
  betaFreqs = np.power(v/vc, beta);  
  out = np.empty([v.size, nterms], dtype=float);
  for i in range(0, nterms):
    out[:,i] = betaFreqs * logFreqs**i;    
  return out;

def linearLogExpansion(v, vc, terms, beta=-2.5):
  components = linearLogExpansionComponents(v, vc, terms.size, beta);
  return components.dot(terms);


# --------------------------------------------------------------------------- #
# Non-linear foreground models
# --------------------------------------------------------------------------- #
  
# Extrapolation of intrinsic foreground contribution to Hills et al. model
def exponentLogExpansion(v, vc, terms):
    normFreqs = v/vc;
    logFreqs = np.log(v/vc);
    out = np.ones_like(v, dtype=float);
    for i in range(1, terms.size):
      out = out * normFreqs**(terms[i] * logFreqs**(i-1));
  
    return terms[0] * out;

# Returns a 2D array (nfreqs, nmodels) of many model realizations.
# terms should be a 2D array (nparams, nmodels).
def exponentLogExpansionSet(v, vc, terms):
  nfreqs = v.size;
  nmodels = terms.shape[1];
  set = np.empty([nfreqs, nmodels], dtype=float);
  for i in range(0, nmodels):
    set[:,i] = exponentLogExpansion(v, vc, terms[:,i]);
  return set;


# --------------------------------------------------------------------------- #
# Ionosphere model
# --------------------------------------------------------------------------- #

# Ionosphere model used in Rogers et al. 2015 consisting of an absorption term
# applied to the intrinsic sky spectrum and an emission term.  This model
# neglects direction-dependent effects (e.g. refraction).
def ionosphereComponents(v, vc, tau, Te):
  normFreqs = v/vc;
  out = np.empty([v.size, 2], dtype=float);
  out[:,0] = np.exp(-1 * tau * normFreqs**(-2));
  out[:,1] = Te * (1 - out[:,0]);
  return out;

def ionosphere(v, vc, intrinsic, tau, Te):
  components = ionosphereComponents(v, vc, tau, Te);
  return intrinsic*components[:,0] + components[:,1];
  

# Provides a set of models combining the exponentLogExpansion model as the
# intrinsic foreground spectrum modified by the ionosphere model. 
def fullSet(v, vc, foregroundTerms, ionTerms):
  nfreqs = v.size;
  nmodels = foregroundTerms.shape[1];
  
  # populate the set with spectra
  set = np.empty([nfreqs, nmodels], dtype=float);
  for i in range(0, nmodels):
    set[:,i] = ionosphere(v, vc, exponentLogExpansion(v, vc, 
       foregroundTerms[:,i]), ionTerms[0,i], ionTerms[1,i]);
  
  return set;
  

# --------------------------------------------------------------------------- #
# Derived foreground models
# --------------------------------------------------------------------------- #

# Creates an orthogonal basis set from a training set of foreground models.
# Similar to Tauscher et al. 2017(?).  Performs an SVD analysis on the supplied 
# training set (nfreqs, nmodels) of models and returns nbasis vectors.
def svdBasis(set, nbasis):
   
  # Calculate the basis vectors
  U, s, Vt = np.linalg.svd(np.transpose(set), full_matrices=False);
  return np.transpose(Vt[range(0,nbasis),:]), s[range(0,nbasis)];


# --------------------------------------------------------------------------- #
# Model fitting
# --------------------------------------------------------------------------- #

# Do a simple linear fit without data covariance matrix
# data (nfreqs), modelComponents(nfreqs, nTerms)
def fitLinear(data, modelComponents):
  fit = np.linalg.lstsq(modelComponents, data, rcond=None);
  return fit[0], np.sqrt(fit[1]/data.shape[0]);

def fitLinearFast(data, modelComponents):
  return np.dot(np.linalg.inv(np.dot(modelComponents.T, modelComponents)), np.dot(modelComponents.T, data));

# Do a linear fit with a covariance matrix
# A diagonal covariance matrix would look like: C = np.diag(yerr * yerr)
def fitLinearCov(data, dataCov, modelComponents):
  cov = np.linalg.inv(np.dot(modelComponents.T, np.linalg.solve(dataCov, modelComponents)));
  fit = np.dot(cov, np.dot(modelComponents.T, np.linalg.solve(dataCov, data)));
  return fit, cov;


# Returns log likelihood for the data and model realization provided.
def logLike(data, dataErr, modelRealization):
    inv_sigma2 = 1.0/(dataErr**2);
    return -0.5*(np.sum((data - modelRealization)**2*inv_sigma2 - np.log(inv_sigma2)));

# Returns 0 or -Inf depending on if all theta are within the  
# bounds given priori = [[min, max], ... ntheta]
def logUniformPriors(theta, priors):
  for (t, p) in zip(theta, priors):
    if (t < p[0] or t>p[1]):
      return -np.Inf;
  return 0;

# foregroundComponents (ndata, nforegroundparams), signalTrials (nsignalparams, ntrials)
def searchSignalTrials(data, foregroundComponents, x, signalFunction, signalTrials, dataCov=None):

  ntrials = signalTrials.shape[1];  
  foregroundFit = np.zeros([foregroundComponents.shape[1], ntrials]);
  rms = np.zeros(ntrials); 

  if dataCov is None:
     for i in range(ntrials):
      signal = signalFunction(x, signalTrials[:,i]);
      foregroundFit[:,i], rms[i] = fitLinear(data - signal, foregroundComponents); 
  else:  
    for i in range(ntrials):
      signal = signalFunction(x, signalTrials[:,i]);
      foregroundFit[:,i], cov = fitLinearCov(data - signal, dataCov, foregroundComponents);
      rms[i] = np.std(data - signal - foregroundComponents.dot(foregroundFit[:,i]));
      
  return foregroundFit, rms;
  
  

# foregroundComponents (ndata, nforegroundparams), signalRealizations(ndata, nrealizations)
def searchSignalRealizations(data, foregroundComponents, x, signalRealizations, dataCov=None):
  
  ntrials = signalRealizations.shape[1];
  foregroundFit = np.zeros([foregroundComponents.shape[1], ntrials]);
  rms = np.zeros(ntrials);
  
  if dataCov is None:
    for i in range(ntrials):
      foregroundFit[:,i], rms[i] = fitLinear(data - signalRealizations[:,i], foregroundComponents);      
  else: 
    for i in range(ntrials):
      foregroundFit[:,i], cov = fitLinearCov(data - signalRealizations[:,i], dataCov, foregroundComponents);
      rms[i] = np.std(data - signalRealizations[:,i] - foregroundComponents.dot(foregroundFit[:,i]));
      
  return foregroundFit, rms;
     

# foregroundComponents (ndata, nforegroundparams), signalRealizations(ndata, nrealizations)
def searchSignalRealizationsFast(data, XTX, XT, signalRealizations):
  
  # Subtract the signal realizations from the data
  subData = (data - signalRealizations.T).T;
  
  # Fit the foreground model to each of the subtracted spectra
  foregroundFit = np.dot(XTX, np.dot(XT, subData));  

  # Make realizations of the best fit foreground models
  realizationFit = np.dot(XT.T, foregroundFit);
  
  # Calculate the residual RMS
  rms = np.sqrt(np.mean((subData - realizationFit)**2, axis=0));
      
  return foregroundFit, rms;

  
# steps is a Python list of lists.  Each sublist contains the values to use
# for the corresponding parameter in the model.
# Returns trials(nparams, ntrials)
def populateGrid(steps):
  nparams = len(steps); 
  lengths = [len(x) for x in steps];
  ntrials = np.prod(lengths);
  blocks = np.insert(np.cumprod(lengths), 0, 1);

  trials = np.empty([nparams, ntrials], dtype=float);  
  for i in range(0, nparams):
    stepIndex = 0;
    trialIndex = 0;
    while (trialIndex < ntrials):
      trials[i, range(trialIndex, trialIndex+blocks[i])] = steps[i][stepIndex];
      stepIndex = (stepIndex + 1) % lengths[i];
      trialIndex = trialIndex + blocks[i];
  return trials; 

# Creates a 2D array of random values (ntrials x nmeans)
def populateRandom(means, sigmas, bounds, ntrials):

  ndim = len(means);
  
  # Create the initial random values for each trial
  vals = [means + sigmas * np.random.randn(ndim) for i in range(ntrials)];

  # Make sure all of our initial values are in the bounds and iterate until
  # they are.
  for i in range(ntrials):
    for j in range(ndim):
      p = bounds[j];
      orig = vals[i][j];
      while not (p[0] < vals[i][j] < p[1]):
        vals[i][j] = means[j] + sigmas[j] * np.random.randn(1);
        
  return vals;


# --------------------------------------------------------------------------- #
# Functions for use with Scipy optimize
# --------------------------------------------------------------------------- #
# result = op.minimize(optFunc, theta_prime, args=(x, y, yerr, ...));
# theta_fit = result["x"];


def optExponentLogExpansion(theta, x, y, yerr, vc):
  return -logLike(y, yerr, exponentLogExpansion(x, vc, theta));

def optLinearLogExpansion(theta, x, y, yerr, vc, beta=-2.5):
  return -logLike(y, yerr, linearLogExpansion(x, vc, theta, beta));   

def optLinearPolynomial(theta, x, y, yerr, vc, beta=-2.5):
  return -logLike(y, yerr, linearPolynomial(x, vc, theta, beta));

def optExponentLogExpansion_FlattenedGaussian(theta, x, y, yerr, vc):
  return -logLike(y, yerr, 
    exponentLogExpansion(x, vc, theta[:-4]) + 
    flattenedGaussian(x, theta[-4:]) );
  
def optLinearPolynomial_FlattenedGaussian(theta, x, y, yerr, vc, beta=-2.5):
  return -logLike(y, yerr, 
    linearPolynomial(x, vc, theta[:-4], beta) + 
    flattenedGaussian(x, theta[-4], theta[-3], theta[-2], theta[-1]) );  
        
def optLinearPhysical_FlattenedGaussian(theta, x, y, yerr, vc):
  return -logLike(y, yerr, 
    linearPhysical(x, vc, theta[:-4]) + 
    flattenedGaussian(x, theta[-4:]) );  
                 
def optLinearLogExpansion_FlattenedGaussian(theta, x, y, yerr, vc, beta=-2.5):
  return -logLike(y, yerr, 
    linearLogExpansion(x, vc, theta[:-4], beta) + 
    flattenedGaussian(x, theta[-4:]) );              
                  
                  
                  
# --------------------------------------------------------------------------- #
# Functions for use with EMCEE (MCMC sampler)
# --------------------------------------------------------------------------- #
                
def probLinearPolynomial(theta, x, y, yerr, vc, beta, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, linearPolynomial(x, vc, beta, theta));                  

def probLinearPolynomial_FlattenedGaussian(theta, x, y, yerr, vc, beta, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, linearPolynomial(x, vc, theta[:-4], beta) +
                      flattenedGaussian(x, theta[-4:])); 

def probLinearPhysical(theta, x, y, yerr, vc, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, linearPhysical(x, vc, theta)); 
     
def probLinearPhysical_FlattenedGaussian(theta, x, y, yerr, vc, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, linearPhysical(x, vc, theta[:-4]) +
                      flattenedGaussian(x, theta[-4:])); 
          
def probLinearLogExpansion(theta, x, y, yerr, vc, beta, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, linearLogExpansion(x, vc, theta, beta));  

def probLinearLogExpansion_FlattenedGaussian(theta, x, y, yerr, vc, beta, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, linearLogExpansion(x, vc, theta[:-4], beta) +
                      flattenedGaussian(x, theta[-4:])); 

def probExponentLogExpansion(theta, x, y, yerr, vc, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, exponentLogExpansion(x, vc, theta)); 

def probExponentLogExpansion_FlattenedGaussian(theta, x, y, yerr, vc, priors=None):
  if priors is None:
    lp = 0;
  else:
    lp = logUniformPriors(theta, priors);
    if not np.isfinite(lp):
      return -np.Inf;
  return lp + logLike(y, yerr, exponentLogExpansion(x, vc, theta[:-4]) +
                      flattenedGaussian(x, theta[-4:])); 
          


# --------------------------------------------------------------------------- #
# File IO Helpers
# --------------------------------------------------------------------------- #

# Get the number of rows in a text/csv file
def numRows(fname):
  with open(fname, 'r') as f:
    for i, l in enumerate(f):
      pass
  return i + 1;
  
  
  
def isFloat(str):
  try:
    float(str);
    return True;
  except ValueError:
    return False;
    
    
# Read a CSV file output by the simulation scripts
def readFile(inputFile):

  # Find out how many rows are in the file
  nrows = numRows(inputFile);
               
  with open(inputFile, "r") as csvFile:
  
    csvReader = csv.reader(csvFile);
    
    for i, row in enumerate(csvReader):
    
      # The first row is a header row with labels for parameters and 
      # frequencies bins
      if i is 0:
      
        # The first columns are usually parameter values so find these
        paramLabels = [s for s in row if not isFloat(s)];
        nparams = len(paramLabels);
        
        # Then the frequencies for the spectra
        freqs = np.array([float(j) for j in row[nparams:]], dtype=float);
        nfreqs = len(freqs);
        
        # Allocate output holders for the data
        params = np.empty([nparams, nrows-1], dtype=float);
        spectra = np.empty([nfreqs, nrows-1], dtype=float);
        
      # The rest of the file is the data
      else:
        params[:,i-1] = row[:nparams];
        spectra[:,i-1] = row[nparams:];
        
  return spectra, freqs, params, paramLabels;


