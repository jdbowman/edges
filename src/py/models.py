"""
Name: sim.py
Desc: Useful functions for simulating EDGES data and analysis
"""

import numpy as np



#def getEDGESpolynomial(freqs, terms):

#def getPhysical(freqs, terms):

#def getLinearPhysical(freqs, terms):

def getQuasiPhysical(v, vc, beta, terms):
  logFreqs = np.log10(v/vc);
  betaFreqs = np.power(v/vc, beta);

  Tsky = np.ones_like(v, dtype=float64);
  for i in range(0,length(terms)):
    Tsky = Tsky + betaFreqs * terms(i) * logFreqs^i;

  return Tsky;

#def applyIono(freqs, tau, Te):

#def getIonoAbsorption(freqs, tau):

#def getIonoEmission(freqs, tau, Te):


