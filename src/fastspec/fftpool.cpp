
#include <algorithm>
#include <stdlib.h>
#include <unistd.h>
#include "fftpool.h"
#include "utility.h"




// ----------------------------------------------------------------------------
// Constructor
// ----------------------------------------------------------------------------
FFTPool::FFTPool(unsigned int uNumThreads, unsigned int uNumBuffers, 
                 unsigned int uNumChannels)
{

  unsigned int i;

  m_uNumThreads = uNumThreads;
  m_uNumBuffers = uNumBuffers;
  m_uNumChannels = uNumChannels;
  m_uNumFFT = 2*m_uNumChannels;
  m_pCallback = NULL;
  m_bStop = false;

  // Allocate space and initialize window function
  m_pWindowHolder = (FFT_REAL_TYPE*) malloc(2*m_uNumFFT*sizeof(FFT_REAL_TYPE));
  for (i=0; i<(2*m_uNumFFT); i++) {
    m_pWindowHolder[i]=1;
  }
  m_uNumTaps = 1;
  for (i=0; i<4; i++) {
    m_pWindow[i] = m_pWindowHolder;
  }

  // Create buffers and push into queue
  printf("FFTPool: Creating %d buffers...\n", m_uNumBuffers);
  for (unsigned int i=0; i<m_uNumBuffers; i++) {
    FFT_REAL_TYPE* pBuffer = (FFT_REAL_TYPE*) FFT_MALLOC(m_uNumFFT * sizeof(FFT_REAL_TYPE));
    if (pBuffer != NULL) {
      m_empty.push(pBuffer);
    } else {
      printf("FFTPool: Failed to create buffer %d of %d.\n", i, m_uNumBuffers);
    }
  }
  printf("Done.\n");

  // Create FFT plan
  //printf("FFTPool: Creating FFT plan...\n");
  //FFT_REAL_TYPE* pTemp = (FFT_REAL_TYPE*) FFT_MALLOC(m_uNumFFT * sizeof(FFT_REAL_TYPE));
  //m_fftPlan = FFT_PLAN(m_uNumFFT, pTemp, pTemp, FFTW_R2HC, FFTW_MEASURE);
  //FFT_FREE(pTemp);
  //printf("Done.\n");

  // Allocate space for thread handles
  printf("FFTPool: Creating %d threads...\n", m_uNumThreads);
  m_pThreads = (pthread_t*) malloc(m_uNumThreads * sizeof(pthread_t));

  // Initialize the mutexes
  pthread_mutex_init(&m_mutexEmpty, NULL);
  pthread_mutex_init(&m_mutexFull, NULL);
  pthread_mutex_init(&m_mutexCallback, NULL);
  pthread_mutex_init(&m_mutexPlan, NULL);

  // Spawn the threads
  for (i=0; i < m_uNumThreads; i++ ) {
    if (pthread_create(&(m_pThreads[i]), NULL, threadLoop, this) != 0 ) {
      printf("FFTPool: Failed to create thread %d of %d.", i, m_uNumThreads);
    } 
  }
  debug("Done.\n");
}



// ----------------------------------------------------------------------------
// Destructor
// ----------------------------------------------------------------------------
FFTPool::~FFTPool()
{
  // Join all of our threads back to us
  m_bStop = true;
  
  for (unsigned int i=0; i<m_uNumThreads; i++) {
    pthread_join(m_pThreads[i], NULL);
  }

  // Free the thread pointers
  free(m_pThreads);

  // Destroy the mutexes
  pthread_mutex_destroy(&m_mutexEmpty);
  pthread_mutex_destroy(&m_mutexFull);
  pthread_mutex_destroy(&m_mutexCallback);
  pthread_mutex_destroy(&m_mutexPlan);

  // Free the buffers and clear the queues
  FFT_REAL_TYPE* pBuffer;

  while (!m_full.empty()) {
    pBuffer = m_full.front();
    m_full.pop();
    FFT_FREE(pBuffer);
  }

  while (!m_empty.empty()) {
    pBuffer = m_empty.front();
    m_empty.pop();
    FFT_FREE(pBuffer);
  }

}



// ----------------------------------------------------------------------------
// setCallback
// ----------------------------------------------------------------------------
void FFTPool::setCallback(fftpool_callback_fptr pCallback)
{
  m_pCallback = pCallback;
}



// ----------------------------------------------------------------------------
// setWindowFunction - Copies provided window function and specifies how many
//                     applications of the window function to use.  
//
//                     uNumTaps:
//
//                       1 - window function is applied once
//                       2 - applied twice, with a 180 degree phase shift for
//                           for the second application
//                       3 - applied three times, with 120 and 240 degree phase
//                           shifts for the second and third applications
//                       4 - applied four times, with 90, 180, and 270 degree
//                           phase shifts for the 2, 3, and 4th applications.
//
//                      For Blackman-Harris window functions, the efficiency of
//                      the first application is ~36%, two applications is 
//                      about ~72%, three is about ~96%, and four is nearly 
//                      100%.
//
//                      Each application requires an addition FFT so the
//                      computational cost scales with applications.
//     
// ----------------------------------------------------------------------------
bool FFTPool::setWindowFunction(FFT_REAL_TYPE* pWindow, unsigned int uLength, 
                                unsigned int uNumTaps)
{
  if ((uLength != m_uNumFFT) || (uNumTaps < 1) || (uNumTaps > 4)) {
    printf("FFTPool: Failed to set window function.\n");
    return false;
  }

  for (unsigned int i=0; i<m_uNumFFT; i++) {
    m_pWindowHolder[i] = pWindow[i];
    m_pWindowHolder[i+m_uNumFFT] = pWindow[i];
  }

  m_uNumTaps = uNumTaps;
  m_pWindow[0] = m_pWindowHolder;

  switch (uNumTaps) 
  {
  case 2:
    m_pWindow[1] = &(m_pWindowHolder[(unsigned int) (0.5 * m_uNumFFT)]);
    break;
  case 3:
    m_pWindow[1] = &(m_pWindowHolder[(unsigned int) (1.0/3.0 * m_uNumFFT)]);
    m_pWindow[2] = &(m_pWindowHolder[(unsigned int) (2.0/3.0 * m_uNumFFT)]);
    break;
  case 4:
    m_pWindow[1] = &(m_pWindowHolder[(unsigned int) (0.25 * m_uNumFFT)]);
    m_pWindow[2] = &(m_pWindowHolder[(unsigned int) (0.5 * m_uNumFFT)]);
    m_pWindow[3] = &(m_pWindowHolder[(unsigned int) (0.75 * m_uNumFFT)]);
    break;  
  }

  return true;
}



// ----------------------------------------------------------------------------
// empty
// ----------------------------------------------------------------------------
bool FFTPool::empty()
{
  pthread_mutex_lock(&m_mutexEmpty);
  bool bEmpty = (m_empty.size() == m_uNumBuffers);
  pthread_mutex_unlock(&m_mutexEmpty);

  return bEmpty;
}



// ----------------------------------------------------------------------------
// waitForEmpty - Returns true when empty.  Returns false if aborted by stop
//                signal.
// ----------------------------------------------------------------------------
bool FFTPool::waitForEmpty()
{
  while (!m_bStop && !empty()) {
    usleep(THREAD_SLEEP_MICROSECONDS);
  }

  return !m_bStop;
}



// ----------------------------------------------------------------------------
// popEmpty -- Thread-safe pop from m_empty queue.  Returns NULL if empty.
// ----------------------------------------------------------------------------
FFT_REAL_TYPE* FFTPool::popEmpty()
{
  FFT_REAL_TYPE* pBuffer = NULL;

  // Check the queue and get a buffer if available  
  pthread_mutex_lock(&m_mutexEmpty);
  if (!m_empty.empty()) {
    pBuffer = m_empty.front();
    m_empty.pop();
  }
  pthread_mutex_unlock(&m_mutexEmpty);

  return pBuffer;
}


// ----------------------------------------------------------------------------
// popFull -- Thread-safe pop from m_full queue.  Returns NULL if empty.
// ----------------------------------------------------------------------------
FFT_REAL_TYPE* FFTPool::popFull()
{
  FFT_REAL_TYPE* pBuffer = NULL;

  // Check the queue and get a buffer if available  
  pthread_mutex_lock(&m_mutexFull);
  if (!m_full.empty()) {
    pBuffer = m_full.front();
    m_full.pop();
  }
  pthread_mutex_unlock(&m_mutexFull);

  return pBuffer;
}



// ----------------------------------------------------------------------------
// pushEmpty -- Thread-safe push to m_empty queue.
// ----------------------------------------------------------------------------
void FFTPool::pushEmpty(FFT_REAL_TYPE* pBuffer)
{
  pthread_mutex_lock(&m_mutexEmpty);
  m_empty.push(pBuffer);
  pthread_mutex_unlock(&m_mutexEmpty);
}



// ----------------------------------------------------------------------------
// pushFull -- Thread-safe push to m_full queue.
// ----------------------------------------------------------------------------
void FFTPool::pushFull(FFT_REAL_TYPE* pBuffer)
{
  pthread_mutex_lock(&m_mutexFull);
  m_full.push(pBuffer);
  pthread_mutex_unlock(&m_mutexFull);
}



// ----------------------------------------------------------------------------
// push -- Copies data into a buffer for processing.  If no buffers are 
//         available, it will return false.
// ----------------------------------------------------------------------------
bool FFTPool::push(unsigned short* pIn, unsigned int uLength)
{
  FFT_REAL_TYPE* pBuffer = NULL;

  if (uLength != m_uNumFFT || m_bStop) {
    return false;
  }

  // Try to get an empty buffer for use
  if ((pBuffer = popEmpty()) == NULL) {
    return false;
  }

  // Copy the incoming data into our buffer
  for (unsigned int i=0; i<m_uNumFFT; i++) {
    pBuffer[i] =  (((FFT_REAL_TYPE) pIn[i]) - 32768.0) / 32768.0;
  }

  // Put the buffer into the processing queue
  pushFull(pBuffer);

  return true;

} // push()



// ----------------------------------------------------------------------------
// threadLoop -- Primary execution loop of each thread
// ----------------------------------------------------------------------------
void* FFTPool::threadLoop(void* pContext)
{
  FFTPool* pPool = (FFTPool*) pContext;
  FFT_REAL_TYPE* pBuffer;

  // Allocate the FFT and final spectrum buffers
  FFT_REAL_TYPE* pLocal1 = (FFT_REAL_TYPE*) FFT_MALLOC(pPool->m_uNumFFT * sizeof(FFT_REAL_TYPE));
  FFT_COMPLEX_TYPE* pLocal2 = (FFT_COMPLEX_TYPE*) FFT_MALLOC((pPool->m_uNumChannels+1) * sizeof(FFT_COMPLEX_TYPE));
  FFT_REAL_TYPE* pLocal3 = (FFT_REAL_TYPE*) FFT_MALLOC((pPool->m_uNumChannels) * sizeof(FFT_REAL_TYPE));

  // Create the FFT plan
  pthread_mutex_lock(&(pPool->m_mutexPlan));
  FFT_PLAN_TYPE pPlan = FFT_PLAN(pPool->m_uNumFFT, pLocal1, pLocal2, FFTW_MEASURE);
  pthread_mutex_unlock(&(pPool->m_mutexPlan));

  //FFT_PLAN_TYPE pPlan = FFT_PLAN(pPool->m_uNumFFT, pLocal1, pLocal2, FFTW_R2HC, FFTW_MEASURE);

  while (!pPool->m_bStop) {

    // Try to get a full buffer that needs processing
    if ((pBuffer = pPool->popFull()) == NULL) {
      usleep(THREAD_SLEEP_MICROSECONDS);
    } else {

      // Process the data in the buffer
      pPool->process(pBuffer, pLocal1, pLocal2, pLocal3, pPlan);
    
      // Release the buffer
      pPool->pushEmpty(pBuffer);
    }
  }

  // Destroy the FFT plan
  FFT_DESTROY_PLAN(pPlan);

  // Release the local buffers
  FFT_FREE(pLocal1);
  FFT_FREE(pLocal2);
  FFT_FREE(pLocal3);

  // Exit the thread
  pthread_exit(NULL);

}



// ----------------------------------------------------------------------------
// process -- Handle a buffer of data
// ----------------------------------------------------------------------------
void FFTPool::process( FFT_REAL_TYPE* pIn, FFT_REAL_TYPE* pLocal1, 
                       FFT_COMPLEX_TYPE* pLocal2, FFT_REAL_TYPE* pLocal3, 
                       FFT_PLAN_TYPE pPlan)
{

  unsigned int i;
  FFT_REAL_TYPE dMax = pIn[0];
  FFT_REAL_TYPE dMin = pIn[0];

  // Reset the sum
  std::fill(pLocal3, pLocal3+m_uNumChannels, 0);

  // Find the ADC max and min
  for (i=0; i<m_uNumFFT; i++) {
    if (pIn[i] < dMin) { 
      dMin = pIn[i]; 
    } else if (pIn[i] > dMax) { 
      dMax = pIn[i]; 
    }
  }


  FFTData sData;

  // For each application of the window function
  for (unsigned int w=0; w<m_uNumTaps; w++) {

    for (i=0; i<m_uNumFFT; i++) {
      pLocal1[i] = pIn[i] * m_pWindow[w][i];
    }

    // Perform the FFT
    FFT_EXECUTE(pPlan);

    // Square and calculate the spectrum 
    // This ignores the nyquist (highest) frequency keeping with preivous 
    // EDGES codes
    for (i = 0; i < m_uNumChannels; i++) 
    { 
      pLocal3[i] = pLocal2[i][0]*pLocal2[i][0] + pLocal2[i][1]*pLocal2[i][1];
    }

    sData.pData = pLocal3;
    sData.uNumChannels = m_uNumChannels;
    sData.dADCmin = dMin;
    sData.dADCmax = dMax;
    sData.uTap = w;

    // Send the resulting spectrum to the callback function for handling
    pthread_mutex_lock(&m_mutexCallback);
    m_pCallback(&sData);
    pthread_mutex_unlock(&m_mutexCallback);
  }
} // process()
