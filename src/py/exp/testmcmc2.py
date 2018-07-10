# -*- coding: utf-8 -*-
import numpy as np
import scipy.optimize as op
import matplotlib.pyplot as plt
import models
import emcee
import corner

# --------------------------------------------------------------------------- #
# Load public EDGS data from Bowman et al. 2018 Figure 1
# G:\My Drive\Publications\Papers\2017_EDGES_Low\PublicData
# --------------------------------------------------------------------------- #

data = np.genfromtxt('G:/My Drive/Publications/Papers/2017_EDGES_Low/PublicData/figure1_plotdata.csv', delimiter=',', skip_header=1);
f = data[:,0];
w = data[:,1];
d = data[:,2];

# Extract frequency coordinates from the data file for small and large subbands
v = [data[(data[:,1]>0),0], data[(data[:,0]>63) & (data[:,0]<99),0]];

# Extract the data for the same ranges
d = [data[(data[:,1]>0),2], data[(data[:,0]>63) & (data[:,0]<99),2]];

# Thermal uncertainty estimate per channel
thermalUncertainty = 0.025;
derr = [thermalUncertainty * np.ones_like(x) for x in v];

# Arguments for functions
runtitle = 'LinearLogExpansion';
vc = 75;
beta = -2.5;
frange = 0;
labels=["a0", "a1", "a2", "a3", "a4", "v0", "w", "tau", "A"];
priors = [[-1e5, 1e5], [-1e5, 1e5], [-1e5, 1e5], [-1e5, 1e5], [-1e5, 1e5], 
          [50, 100], [1, 100], [0.01, 100], [-1e5, 1e5]];
          
guess_mean = [1500, 1, 1, 1, 1,   65, 10, 1, 0];
guess_sigma = [500, 500, 500, 500, 500,    10, 10, 1, 1];

#args = (v[frange], d[frange], derr[frange], vc, priors);
args = (v[frange], d[frange], derr[frange], vc, beta, priors);

# Configure the sampler
ndim = np.size(guess_mean);
nwalkers = 200;
niter = 20000;

# Create the starting guess for each walker
pos = models.populateRandom(guess_mean, guess_sigma, priors, nwalkers);

# Standard sampler      
#sampler = emcee.EnsembleSampler(nwalkers, 
#                                ndim, 
#                                models.probLinearLogExpansion_FlattenedGaussian, 
#                                args=args);
                  
# Parallel Tempered sampler for multi-modal systems  
ntemps = 8;  
pargs = [priors]; 

pos = [models.populateRandom(guess_mean, guess_sigma, priors, nwalkers) for i in range(ntemps)];
  
sampler = emcee.PTSampler(ntemps,
                          nwalkers, 
                          ndim, 
                          models.probLinearLogExpansion_FlattenedGaussian,
                          models.logUniformPriors,
                          loglargs=(v[frange], d[frange], derr[frange], vc, beta),
                          logpargs=pargs,
                          loglkwargs={'priors':None});

# Run the sampler
sampler.run_mcmc(pos, niter);

nburn = 19000;
temp = 0;
samples = sampler.chain[temp,:,nburn:,:].reshape((-1, ndim));

# Get the best fits and confidence ranges (68%)
params_mcmc = list(map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]), 
                  zip(*np.percentile(samples, [16, 50, 84], axis=0))));

 
# Plot the chains
for i in range(ndim):
  plt.figure(i);
  plt.clf();
  plt.plot(sampler.chain[temp, :,0:-1:10,i].transpose(), 'k-', linewidth=0.1);
  plt.show();
  plt.savefig('G:/My Drive/EDGES/mcmc/{}_temp{}_param{}.png'.format(runtitle, temp, i));
  
fig, axes = plt.subplots(ndim, ndim, figsize=(14, 9));
corner.corner(samples, labels=["$a0$", "$a1$", "$a2$", "a3", "a4", "v0", "w", "tau", "A"], fig=fig);
plt.savefig('G:/My Drive/EDGES/mcmc/{}_temp{}_corner.png'.format(runtitle, temp));

with open('G:/My Drive/EDGES/mcmc/{}_temp{}_results.txt'.format(runtitle, temp), "w") as text_file:
  print("beta = {}".format(beta), file=text_file);
  print("vc = {}".format(vc), file=text_file);
  print("labels = {}".format(labels), file=text_file);
  print("priors = {}".format(priors), file=text_file);
  print("guess_mean = {}".format(guess_mean), file=text_file);
  print("guess_sigma = {}".format(guess_sigma), file=text_file);
  print("ntemps = {}".format(ntemps), file=text_file);
  print("nwalkers = {}".format(nwalkers), file=text_file);
  print("niter = {}".format(niter), file=text_file);
  print("nburn = {}".format(nburn), file=text_file);
  print("frequency (min, max) = ({}, {})".format(np.min(v[frange]), np.max(v[frange])), file=text_file);

  for a,p in zip(labels, params_mcmc):
    print("Param {0}: {1:6.4f} +/- ({2:6.4f}, {3:6.4f})".format(a, p[0], p[1], p[2]));
    print("Param {0}: {1:6.4f} +/- ({2:6.4f}, {3:6.4f})".format(a, p[0], p[1], p[2]), file=text_file);

fit = np.array([p[0] for p in params_mcmc]);
foreground = models.linearLogExpansion(v[frange], vc, beta, fit[:-4]);
signal = models.flattenedGaussian(v[frange], fit[-4], fit[-3], fit[-2], fit[-1]);
residuals = d[frange] - foreground - signal;
rms = np.std(residuals);
print("RMS residual: {0:6.4f} K".format(rms));

plt.figure(ndim+1);
plt.clf();
plt.plot(v[frange], residuals);
plt.xlabel('Frequency [MHz]');
plt.ylabel('T [K]');
plt.title("RMS residual: {0:6.4f}".format(rms));
plt.savefig('G:/My Drive/EDGES/mcmc/{}_temp{}_residuals.png'.format(runtitle, temp, i));