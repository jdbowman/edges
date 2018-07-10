# -*- coding: utf-8 -*-
import numpy as np
import scipy.optimize as op
import matplotlib.pyplot as plt
import models

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
vc = 75;
beta = -2.5;
frange = 1;
known_signal = [models.flattenedGaussian(v[i], 79, 19, 6.5, -0.5) for i in range(0,len(v))];
args_vc = [(v[i], d[i], derr[i], vc) for i in range(0,len(v))];
args_vc_beta = [(v[i], d[i] - known_signal[i], derr[i], vc, beta) for i in range(0,len(v))];

# Find solutions

#theta_prime = [1700, -2.5, 0, 0,   79, 19, 7, -0.5]; # exponentLogExpansion_FlattenedGaussian
#result = op.minimize(models.optExponentLogExpansion_FlattenedGaussian, theta_prime, args=args_vc[frange]);

#theta_prime = [1700, -2.5, 0, 0, 0]; # exponentLogExpansion
#result = op.minimize(models.optExponentLogExpansion, theta_prime, args=args_vc[frange]);

nterms = 5;
theta_prime = [1792, 127, -276, 123, -16,   79, 19, 7, -0.5]; # linearPolynomial_FlattenedGaussian
bounds = [[None, None], [None, None], [None, None], [None, None], [None, None], [75, 83], [10, 30], [1, 10], [-2, -0.1]];
result = op.minimize(models.optLinearPolynomial_FlattenedGaussian, theta_prime, 
                     args=args_vc_beta[frange],
                     tol = 1e-6,
                     method='Nelder-Mead');

#theta_prime = [1700, 0, 0, 0, 0]; # linearPolynomial
#result = op.minimize(models.optLinearPolynomial, theta_prime, args=args_vc_beta[frange]);

#nterms = 5;
#theta_prime = [1700, 0, 0, 0, 0,    79, 19, 7, -0.5]; # linearLogExpansion_FlattenedGaussian
#bounds = [[1000, 2000], [-5000, 10], [-5000, 10], [-5000, 10], [-5000, 1000], [75, 83], [10, 30], [5, 10], [-0.8, -0.3]];
#result = op.minimize(models.optLinearLogExpansion_FlattenedGaussian, 
#                     theta_prime, 
#                     bounds = bounds,
#                     args=args_vc_beta[frange],
#                     tol = 1e-10,
#                     method='L-BFGS-B',
#                     options={'eps':1e-8, 'maxcor': 100, 'gtol':1e-9, 'ftol':1e-12, 'maxls':1000, 'maxiter': 100000, 'disp': True});

#nterms = 5;
#theta_prime = [1500, 0.1, 0.1, 0.1, 0.1]; # linearLogExpansion
#result = op.minimize(models.optLinearLogExpansion, theta_prime, args=args_vc_beta[frange]);

# Extract the fit

fit_min = result["x"];
fit_lin, rms_lin_o = models.fitLinear(d[frange] - known_signal[frange], models.linearPolynomialComponents(v[frange],vc,beta,nterms));
fit_linc, cov_linc = models.fitLinearCov(d[frange], np.diag(derr[frange]*derr[frange]), models.linearPolynomialComponents(v[frange],vc,beta,nterms));

#signal = np.zeros_like(v[frange]);
signal = models.flattenedGaussian(v[frange], fit_min[-4], fit_min[-3], fit_min[-2], fit_min[-1]);

model_min = models.linearPolynomial(v[frange], vc, beta, fit_min) + signal;
model_lin = models.linearPolynomial(v[frange], vc, beta, fit_lin);
model_linc = models.linearPolynomial(v[frange], vc, beta, fit_linc);

residuals_min = d[frange] - model_min;
residuals_lin = d[frange] - model_lin;
residuals_linc = d[frange] - model_linc;

rms_min = np.std(residuals_min);
rms_lin = np.std(residuals_lin);
rms_linc = np.std(residuals_linc);

print("RMS minimize fit: {}".format(rms_min));
print("RMS linear fit: {}".format(rms_lin));
print("RMS linear cov fit: {}".format(rms_linc));


plt.figure(1);
plt.clf();
plt.plot(v[frange], residuals_min, v[frange], residuals_lin, v[frange], residuals_linc);
plt.show();

plt.figure(2);
plt.clf();
plt.plot(v[frange], signal);
plt.show();

plt.figure(3);
plt.clf();
plt.plot(v[frange], model_min, v[frange], model_lin, v[frange], model_linc);
plt.show();
