#ifndef _ACCUMULATOR_H_
#define _ACCUMULATOR_H_

#include <stdlib.h>
#include "timing.h"

// ---------------------------------------------------------------------------
//
// ACCUMULATOR
//
// Class that encapsulates a spectrum and some ancillary information.  It is
// intended to facilitate accumulating spectra in place through the "add" 
// member function. 
//
// ---------------------------------------------------------------------------

#define ACCUM_TYPE double // or float

class Accumulator {

  private:

    // Member variables
    ACCUM_TYPE*     m_pSpectrum;
    unsigned int    m_uDataLength;
    unsigned int    m_uNumAccums;
    double          m_dADCmin;
    double          m_dADCmax;
    double          m_dStartFreq;
    double          m_dStopFreq;
    double          m_dChannelFactor;
    double          m_dTemperature;
    TimeKeeper      m_startTime;
    TimeKeeper      m_stopTime;

  public:

    // Constructor and destructor
    
    Accumulator() : m_pSpectrum(NULL), m_uDataLength(0), m_uNumAccums(0), 
                    m_dADCmin(0), m_dADCmax(0), m_dStartFreq(0), m_dStopFreq(0), 
                    m_dChannelFactor(0), m_dTemperature(0) { }
    
    ~Accumulator()
    {
      if (m_pSpectrum) {
        free(m_pSpectrum);
        m_pSpectrum = NULL;
      }
    }


    // Public functions
    
    void add(double dValue) {
      for (unsigned int i=0; i<m_uDataLength; i++) {
        m_pSpectrum[i] += dValue;
      }
    }

    template<typename T>
    bool add(const T* pSpectrum, unsigned int uLength, double dADCmin, double dADCmax) 
    {

      // Abort if there isn't valid data to include
      if ((pSpectrum == NULL) || (uLength != m_uDataLength)) {
        printf("Failed to add spectrum to accumulation.\n");
        return false;
      }

      // Update the ADC min/max record
      m_dADCmin = (dADCmin < m_dADCmin) ? dADCmin : m_dADCmin;
      m_dADCmax = (dADCmax > m_dADCmax) ? dADCmax : m_dADCmax;

      // Increment the block counter
      m_uNumAccums++;

      // Add the new spectrum to the accumulation 
      for (unsigned int n=0; n<uLength; n++) {
        m_pSpectrum[n] += pSpectrum[n];
      }

      return true;
    }
    
    void clear() 
    {
      // Set the spectrum to zeros
      for (unsigned int i=0; i<m_uDataLength; i++) {
        m_pSpectrum[i] = 0;
      }

      // Set the supporting spectrum info parameters to zeros
      m_uNumAccums = 0;
      m_dADCmin = 0;
      m_dADCmax = 0;
      m_startTime.set(0);
      m_stopTime.set(0);
      m_dTemperature = 0;
    }

    ACCUM_TYPE get(unsigned int iIndex) 
    { 
      if (m_pSpectrum) {
        return m_pSpectrum[iIndex]; 
      } else {
        return 0;
      }
    }

    ACCUM_TYPE getADCmin() { return m_dADCmin; }
    
    ACCUM_TYPE getADCmax() { return m_dADCmax; }
    
    ACCUM_TYPE getChannelFactor() { return m_dChannelFactor; }

    bool getCopyOfSum(ACCUM_TYPE* pOut, unsigned int uLength) 
    { 
      if ((pOut == NULL) || (uLength != m_uDataLength)) {
        return false;
      }

      for (unsigned int i=0; i<m_uDataLength; i++) {
        pOut[i] = m_pSpectrum[i];
      }

      return true;
    }

    bool getCopyOfAverage(ACCUM_TYPE* pOut, unsigned int uLength) 
    { 
      double dNormalize = 0;

      if ((pOut == NULL) || (uLength != m_uDataLength)) {
        return false;
      }

      if (m_uNumAccums > 0) {
        dNormalize = 1.0 / (double) m_uNumAccums;
      }

      for (unsigned int i=0; i<m_uDataLength; i++) {
        pOut[i] = m_pSpectrum[i] * dNormalize;
      }

      return true;
    }
    
    unsigned int getDataLength() { return m_uDataLength; }

    unsigned int getNumAccums() { return m_uNumAccums; }

    double getStartFreq() { return m_dStartFreq; }
    
    double getStopFreq() { return m_dStopFreq; }

    TimeKeeper getStartTime() { return m_startTime; }
    
    TimeKeeper getStopTime() { return m_stopTime; }
    
    ACCUM_TYPE* getSum() { return m_pSpectrum; }

    ACCUM_TYPE getTemperature() { return m_dTemperature; }

    void init(unsigned int uDataLength, double dStartFreq, double dStopFreq, 
              double dChannelFactor) 
    { 
      m_pSpectrum = (ACCUM_TYPE*) malloc(uDataLength * sizeof(ACCUM_TYPE));
      m_uDataLength = uDataLength;
      m_dStartFreq = dStartFreq;
      m_dStopFreq = dStopFreq;
      m_dChannelFactor = dChannelFactor;
      clear();
    }

    void multiply(double dValue) {
      for (unsigned int i=0; i<m_uDataLength; i++) {
        m_pSpectrum[i] *= dValue;
      }
    }

    void setStartTime() { m_startTime.setNow(); }
    
    void setStopTime() { m_stopTime.setNow(); }

    void setTemperature(double dTemperature) { m_dTemperature = dTemperature; }


};


#endif // _ACCUMULATOR_H_
