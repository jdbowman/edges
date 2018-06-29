
#include "spectrometer.h"
#include "timing.h"
#include "utility.h"



// ----------------------------------------------------------------------------
// Constructor
// ----------------------------------------------------------------------------
Spectrometer::Spectrometer(unsigned long uNumChannels, 
                           unsigned long uNumSamplesPerAccumulation, 
                           double dBandwidth,
                           bool bWriteTaps,
                           Digitizer* pDigitizer,
                           FFTPool* pFFT,
                           Switch* pSwitch,
                           bool* pbGlobalStop)
{

  using namespace std::placeholders;

  // User specified configuration
  m_uNumChannels = uNumChannels;
  m_uNumSamplesPerAccumulation = uNumSamplesPerAccumulation;
  m_dBandwidth = dBandwidth;
  m_bWriteTaps = bWriteTaps;

  // Derived configuration
  m_dChannelSize = m_dBandwidth / (double) m_uNumChannels; // MHz
  m_dAccumulationTime = (double) uNumSamplesPerAccumulation / m_dBandwidth / 2.0; // seconds
  m_dStartFreq = 0.0;
  m_dStopFreq = m_dBandwidth;
  m_dChannelFactor = 4; // because of Blackmann Harris (should really be closer to 3)

  // Assign the Spectrometer instance's process function to the Digitizer
  // callback on data transfer.
  m_pDigitizer = pDigitizer;
  m_pDigitizer->setCallback(std::bind( &Spectrometer::onTransfer, 
                                this, _1, _2, _3 ) );

  // Remember the receiver switch controller
  m_pSwitch = pSwitch;

  // Initialize the Accumulators
  for (int i=0; i<3; i++) {
    m_accumAntenna[i].init( m_uNumChannels, m_dStartFreq, 
                     m_dStopFreq, m_dChannelFactor );
    m_accumAmbientLoad[i].init( m_uNumChannels, m_dStartFreq, 
                     m_dStopFreq, m_dChannelFactor );
    m_accumHotLoad[i].init( m_uNumChannels, m_dStartFreq, 
                     m_dStopFreq, m_dChannelFactor );
  }
  m_pCurrentAccum = NULL;

  // Setup the stop flags
  m_bLocalStop = false;
  m_pbGlobalStop = pbGlobalStop;

  // Initialize the FFT pool
  m_uNumFFT = 2*m_uNumChannels;
  m_pFFT = pFFT;
  m_pFFT->setCallback(std::bind( &Spectrometer::onSpectrum, this, _1 ) );

  m_uDrops = 0;

} // constructor



// ----------------------------------------------------------------------------
// Destructor
// ----------------------------------------------------------------------------
Spectrometer::~Spectrometer()
{

} // destructor



// ----------------------------------------------------------------------------
// setOutput
// ----------------------------------------------------------------------------
void Spectrometer::setOutput(const string& sOutput, const string& sInstrument, bool bDirectory)
{
  printf("Spectrometer: setOutput: %s\n", sOutput.c_str());

  m_sOutput = sOutput;
  m_sInstrument = sInstrument;
  m_bDirectory = bDirectory;
}



// ----------------------------------------------------------------------------
// getFileName
// ----------------------------------------------------------------------------
string Spectrometer::getFileName()
{

  if (m_bDirectory)
  {
    TimeKeeper startTime = m_accumAntenna[0].getStartTime();
    string sDateString = startTime.getFileString(2);
    string sFilePath = m_sOutput + "/" + to_string(startTime.year()) + "/" 
                        + sDateString + "_" + m_sInstrument + ".acq";
    return sFilePath;

  } else {
    return m_sOutput + ".acq";
  }
}


// ----------------------------------------------------------------------------
// getFileName
// ----------------------------------------------------------------------------
string Spectrometer::getFileName(unsigned int uTap)
{

  if (m_bDirectory)
  {
    TimeKeeper startTime = m_accumAntenna[0].getStartTime();
    string sDateString = startTime.getFileString(2);
    string sFilePath = m_sOutput + "/" + to_string(startTime.year()) + "/" + sDateString + "_tap" + std::to_string(uTap) + "_" + m_sInstrument + ".acq";
    return sFilePath;

  } else {
    return m_sOutput + "_tap" + std::to_string(uTap) + ".acq";
  }
}



// ----------------------------------------------------------------------------
// run() - Main executable function for the EDGES spectrometer
// ----------------------------------------------------------------------------
void Spectrometer::run()
{ 
  m_bLocalStop = false;
  Timer dutyCycleTimer;
  Timer writeTimer;
  TimeKeeper tk;
  double dDutyCycle_Overall;
  double dDutyCycle_FFT;

  if ((m_pDigitizer == NULL) || (m_pSwitch == NULL)) {
    printf("Spectrometer: No digitizer or switch object at start of run.  End.");
    return;
  }

  // Loop until a stop signal is received
  while (!isStop()) {

    dutyCycleTimer.tic();

    // Cycle between switch states
    for (unsigned int i=0; i<3; i++) {

      tk.setNow();
      printf("Spectrometer: Starting switch state %d at %s\n", i, tk.getDateTimeString(5).c_str());

      // Change receiver switch state and pause briefly for it to take effect
      m_pSwitch->set(i);

      // Wait for previous FFTs to finish
      m_pFFT->waitForEmpty();

      // Reset the drop counter
      m_uDrops = 0;

      // Reset the accumulator and record the start time
      switch(i) {
        case 0:
          m_pCurrentAccum = m_accumAntenna;
          break;
        case 1:
          m_pCurrentAccum = m_accumAmbientLoad;
          break;
        case 2:
          m_pCurrentAccum = m_accumHotLoad;
          break;
      }

      for (unsigned int w=0; w<m_pFFT->getNumTaps(); w++) {
        m_pCurrentAccum[w].clear();
        m_pCurrentAccum[w].setStartTime();
      }

      // Acquire data
      m_pDigitizer->acquire(m_uNumSamplesPerAccumulation);

      // Note the stop time
      for (unsigned int w=0; w<m_pFFT->getNumTaps(); w++) {
        m_pCurrentAccum[w].setStopTime();
      }
    }

    // Wait for any remaining FFT processes to finish
    m_pFFT->waitForEmpty();


    // Normalize ADCmin and ADCmax:  we divide adcmin and adcmax by 2 here to  
    // be backwards compatible with pxspec.  This limits adcmin and adcmax to 
    // +/- 0.5 rather than +/-1.0
    for (unsigned int w=0; w<m_pFFT->getNumTaps(); w++) {

      m_accumAntenna[w].setADCmin(m_accumAntenna[w].getADCmin()/2);
      m_accumAntenna[w].setADCmax(m_accumAntenna[w].getADCmax()/2);
      m_accumAmbientLoad[w].setADCmin(m_accumAmbientLoad[w].getADCmin()/2);
      m_accumAmbientLoad[w].setADCmax(m_accumAmbientLoad[w].getADCmax()/2);
      m_accumHotLoad[w].setADCmin(m_accumHotLoad[w].getADCmin()/2);
      m_accumHotLoad[w].setADCmax(m_accumHotLoad[w].getADCmax()/2);
    }

    // Write to ACQ
    writeTimer.tic();

    if (m_bWriteTaps) {

      // Write each tap to a separate file
      for (unsigned int w=0; w<m_pFFT->getNumTaps(); w++) {
        printf("\nSpectrometer: Writing cycle data to file: %s\n", getFileName(w).c_str());
        write_switch_cycle(getFileName(w), m_accumAntenna[w], m_accumAmbientLoad[w], m_accumHotLoad[w]);      
      }

    } else {

      // Co-add spectra from all taps
      if (m_pFFT->getNumTaps() > 1)
      {
        for (unsigned int w=1; w<m_pFFT->getNumTaps(); w++) {
          m_accumAntenna[0].combine(&m_accumAntenna[w]);
          m_accumAmbientLoad[0].combine(&m_accumAmbientLoad[w]);
          m_accumHotLoad[0].combine(&m_accumHotLoad[w]);
        }
      }

      // Write to single file
      printf("\nSpectrometer: Writing cycle data to file: %s\n", getFileName().c_str());
      write_switch_cycle(getFileName(), m_accumAntenna[0], m_accumAmbientLoad[0], m_accumHotLoad[0]);      
    }

    writeTimer.toc();

    // Calculate overall duty cycle
    dutyCycleTimer.toc();
    dDutyCycle_Overall = 3.0 * m_uNumSamplesPerAccumulation / (2.0 * 1e6 * m_dBandwidth) / dutyCycleTimer.get();
    dDutyCycle_FFT = 1.0 * m_uNumSamplesPerAccumulation / (m_uNumSamplesPerAccumulation + m_uDrops); 

    printf("Spectrometer: Cycle time  = %6.3f seconds\n", dutyCycleTimer.get());
    printf("Spectrometer: Switch time = %6.3f seconds\n", 3*SWITCH_SLEEP_MICROSECONDS/1e6);
    printf("Spectrometer: Write time  = %6.3f seconds\n", writeTimer.get());
    printf("Spectrometer: Duty cycle  = %6.3f\n", dDutyCycle_Overall);
    printf("Spectrometer: Drop fraction = %6.3f\n", 1.0 * m_uDrops / (m_uNumSamplesPerAccumulation + m_uDrops));
    printf("Spectrometer: p0 (antenna) -- acdmin = %6.3f,  adcmax = %6.3f\n", m_accumAntenna[0].getADCmin(), m_accumAntenna[0].getADCmax());
    printf("Spectrometer: p1 (ambient) -- acdmin = %6.3f,  adcmax = %6.3f\n", m_accumAmbientLoad[0].getADCmin(), m_accumAmbientLoad[0].getADCmax());
    printf("Spectrometer: p2 (hot)     -- acdmin = %6.3f,  adcmax = %6.3f\n", m_accumHotLoad[0].getADCmin(), m_accumHotLoad[0].getADCmax());
    
    printf("\n");
  }

} // run()




// ----------------------------------------------------------------------------
// sendStop() 
// ----------------------------------------------------------------------------
void Spectrometer::sendStop() 
{
  m_bLocalStop = true;
}



// ----------------------------------------------------------------------------
// isStop() 
// ----------------------------------------------------------------------------
bool Spectrometer::isStop() 
{
  if (m_bLocalStop) {
    return true;
  }

  if (m_pbGlobalStop) {
    if (*m_pbGlobalStop) {
      return true;
    }
  }

  return false;
} // isStop()



// ----------------------------------------------------------------------------
// onTransfer() -- Do something with transferred data.  This function ignores
//                 any transferred data at the end of the transfer beyond the
//                 last integer multiple of m_uNumFFT.  If an FFTPool buffer is 
//                 not available for a given chunk of the transfer, it drops 
//                 that chunk of data.  Returns total number of samples 
//                 successfully processed into an FFTPool buffer.
// ----------------------------------------------------------------------------
unsigned long Spectrometer::onTransfer( unsigned short* pBuffer, 
                                        unsigned int uBufferLength,
                                        unsigned long uTransferredSoFar ) 
{
  unsigned int uIndex = 0;
  unsigned int uAdded = 0;
  unsigned int uDropped = 0;

  // Loop over the transferred data and enter it into the FFTPool buffer
  while ( ((uIndex + m_uNumFFT) <= uBufferLength) 
         && (uTransferredSoFar < m_uNumSamplesPerAccumulation)) {
    

    // Try to add to the FFTPool buffer
    if (m_pFFT->push(&(pBuffer[uIndex]), m_uNumFFT)) { 

      uTransferredSoFar += m_uNumFFT;
      uAdded++;

    } else {

      // No buffers were available so we'll drop the chunk and move on
      uDropped++;
    }

    // Increment the index to the next chunk of transferred data
    uIndex += m_uNumFFT;
  }

  // Keep a permanent record of how many samples were dropped
  m_uDrops += uDropped * m_uNumFFT;

  // Return the total number of transferred samples that were successfully
  // entered in the FFTPool buffer for processing.
  return uAdded * m_uNumFFT;

} // onTransfer()




// ----------------------------------------------------------------------------
// onSpectrum() -- Do something with a spectrum returned from the FFTPool
// ----------------------------------------------------------------------------
void Spectrometer::onSpectrum(const FFTData* pData) 
{  
  m_pCurrentAccum[pData->uTap].add(pData->pData, pData->uNumChannels, pData->dADCmin, pData->dADCmax);
} // onSpectrum()
