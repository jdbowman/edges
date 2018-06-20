#ifndef _SPECTROMETER_H_
#define _SPECTROMETER_H_

#include <string>
#include <functional>
#include "accumulator.h"
#include "digitizer.h"
#include "fftpool.h"
#include "switch.h"

// ---------------------------------------------------------------------------
//
// SPECTROMETER
//
// Uses PXBoard, Switch, and FFTPool objects to control and acquire data from
// the EDGES system.
//
// ---------------------------------------------------------------------------
class Spectrometer {

  private:

    // Member variables
    Digitizer*      m_pDigitizer;
    FFTPool*        m_pFFT;
    Switch*         m_pSwitch;
    Accumulator     m_accum[3];
    Accumulator*    m_pCurrentAccum;
    unsigned long   m_uNumFFT;
    unsigned long   m_uNumChannels;
    unsigned long   m_uNumSamplesPerAccumulation;
    double          m_dAccumulationTime;        // seconds
    double          m_dBandwidth;               // MHz
    double          m_dChannelSize;             // MHz
    double          m_dChannelFactor;    
    double          m_dStartFreq;               // MHz
    double          m_dStopFreq;                // MHz
    bool            m_bLocalStop;
    bool*           m_pbGlobalStop;
    unsigned long   m_uDrops;
    std::string     m_sOutput;
    bool            m_bDirectory;


    // Private helper functions
    bool isStop();
    std::string getFileName();

  public:

    // Constructor and destructor
    Spectrometer( unsigned long, unsigned long, double, 
                  Digitizer*, FFTPool*, Switch*, bool* );
    ~Spectrometer();

    // Execution functions
    void run();
    void sendStop();

    void setOutput(const string&, bool);

    // Callbacks
    unsigned long onTransfer(unsigned short*, unsigned int, unsigned long);
    void onSpectrum(FFT_REAL_TYPE*, unsigned int, double, double);

};



#endif // _SPECTROMETER_H_