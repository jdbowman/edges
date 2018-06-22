
#include "spectrometer.h"
#include "timing.h"
#include "utility.h"



// ----------------------------------------------------------------------------
// Constructor
// ----------------------------------------------------------------------------
Spectrometer::Spectrometer(unsigned long uNumChannels, 
                           unsigned long uNumSamplesPerAccumulation, 
                           double dBandwidth,
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
void Spectrometer::setOutput(const string& sOutput, bool bDirectory)
{
  printf("Spectrometer: setOutput: %s\n", sOutput.c_str());

  m_sOutput = sOutput;
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
                        + sDateString + ".acq";
    return sFilePath;

  } else {
    return m_sOutput;
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
    string sFilePath = m_sOutput + "/" + to_string(startTime.year()) + "/" + sDateString + "_tap" + std::to_string(uTap) + ".acq";
    return sFilePath;

  } else {
    return m_sOutput;
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

      printf("Spectrometer: Starting switch state %d...\n", i);

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
        case 1:
          m_pCurrentAccum = m_accumAmbientLoad;
        case 2:
          m_pCurrentAccum = m_accumHotLoad;
      }

      for (unsigned int w=0; w<m_pFFT->getNumWindows(); w++) {
        m_pCurrentAccum[w].clear();
        m_pCurrentAccum[w].setStartTime();
      }
      
      // Acquire data
      m_pDigitizer->acquire(m_uNumSamplesPerAccumulation);

      // Note the stop time
      for (unsigned int w=0; w<m_pFFT->getNumWindows(); w++) {
        m_pCurrentAccum[w].setStopTime();
      }
    }

    // Wait for any remaining FFT processes to finish
    m_pFFT->waitForEmpty();

    // Normalize the accumulation if we used multiple window function taps.  This
    // keeps the output values at a consistent level regardless of number of
    // window taps applied (done here rather than in FFTPool to reduce overall
    // computations since it only needs to be done once here).
    //if (m_pFFT->getNumWindows() > 1) {
    //  m_accum[0].multiply(1.0 / m_pFFT->getNumWindows());
    //  m_accum[1].multiply(1.0 / m_pFFT->getNumWindows());
    //  m_accum[2].multiply(1.0 / m_pFFT->getNumWindows());
    //}

    // Write to ACQ
    printf("\nSpectrometer: Writing cycle data to file...\n");
    writeTimer.tic();
    for (unsigned int w=0; w<m_pFFT->getNumWindows(); w++) {
      write_switch_cycle(getFileName(w), m_accumAntenna[w], m_accumAmbientLoad[w], m_accumHotLoad[w]);      
    }
    writeTimer.toc();

    // Calculate overall duty cycle
    dutyCycleTimer.toc();
    dDutyCycle_Overall = 3.0 * m_uNumSamplesPerAccumulation / (2.0 * 1e6 * m_dBandwidth) / dutyCycleTimer.get();
    dDutyCycle_FFT = 1.0 * m_uNumSamplesPerAccumulation / (m_uNumSamplesPerAccumulation + m_uDrops); 

    printf("Spectrometer: Cycle time = %6.3f seconds\n", dutyCycleTimer.get());
    printf("Spectrometer: Write time = %6.3f seconds\n", writeTimer.get());
    printf("Spectrometer: Duty cycle = %6.3f\n", dDutyCycle_Overall);
    printf("Spectrometer: Drop fraction = %6.3f\n\n", 1.0 * m_uDrops / (m_uNumSamplesPerAccumulation + m_uDrops));
    printf("Spectrometer: Accumulated spectrum at B/3 (p0, p1, p2) = %8.3f, %8.3f, %8.3f\n", 
       m_accumAntenna[0].get(m_uNumChannels/3),
       m_accumAmbientLoad[0].get(m_uNumChannels/3),
       m_accumHotLoad[0].get(m_uNumChannels/3));
    for (unsigned int i=0; i<3; i++) {
      printf("Spectrometer: p%d acdmin, adcmax = %6.3f, %6.3f\n", i, m_accumAntenna[0].getADCmin(), m_accumAntenna[0].getADCmax());
    }
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
