#ifndef _FFTPOOL_H_
#define _FFTPOOL_H_

#include <functional>
#include <fftw3.h>
#include <pthread.h>
#include <queue>

#ifdef FFT_SINGLE_PRECISION
  #define FFT_REAL_TYPE           float
  #define FFT_COMPLEX_TYPE        fftwf_complex
  #define FFT_PLAN_TYPE           fftwf_plan
  #define FFT_EXECUTE             fftwf_execute
  #define FFT_PLAN                fftwf_plan_dft_r2c_1d
  #define FFT_DESTROY_PLAN        fftwf_destroy_plan
  #define FFT_MALLOC              fftwf_malloc
  #define FFT_FREE                fftwf_free
#else
  #define FFT_REAL_TYPE           double
  #define FFT_COMPLEX_TYPE        fftw_complex
  #define FFT_PLAN_TYPE           fftw_plan
  #define FFT_EXECUTE             fftw_execute
  #define FFT_PLAN                fftw_plan_dft_r2c_1d
  #define FFT_DESTROY_PLAN        fftw_destroy_plan
  #define FFT_MALLOC              fftw_malloc
  #define FFT_FREE                fftw_free
#endif


struct FFTData {
  FFT_REAL_TYPE* pData;
  unsigned int uNumChannels;
  double dADCmin;
  double dADCmax;
  unsigned int uTap;
};


#define fftpool_callback_fptr   std::function<void(const FFTData*)>

#define THREAD_SLEEP_MICROSECONDS 5

using namespace std;

class FFTPool {

  private:

    // Member variables
    fftpool_callback_fptr   m_pCallback;
    pthread_t*              m_pThreads;
    pthread_mutex_t         m_mutexPlan;
    pthread_mutex_t         m_mutexCallback;
    pthread_mutex_t         m_mutexEmpty;
    pthread_mutex_t         m_mutexFull;
    queue<FFT_REAL_TYPE*>   m_empty;
    queue<FFT_REAL_TYPE*>   m_full;
    FFT_REAL_TYPE*          m_pWindowHolder;
    FFT_REAL_TYPE*          m_pWindow[4];
    unsigned int            m_uNumTaps;
    unsigned int            m_uNumThreads;
    unsigned int            m_uNumBuffers;
    unsigned int            m_uNumChannels;
    unsigned int            m_uNumFFT;
    bool                    m_bStop;
    
    // Private helper functions
    FFT_REAL_TYPE*  popEmpty();
    void            pushEmpty(FFT_REAL_TYPE*);
    FFT_REAL_TYPE*  popFull();
    void            pushFull(FFT_REAL_TYPE*);
    void            process(FFT_REAL_TYPE*, FFT_REAL_TYPE*, FFT_COMPLEX_TYPE*, 
                            FFT_REAL_TYPE*, FFT_PLAN_TYPE);

  public:

    // Constructor and destructor
    FFTPool(unsigned int, unsigned int, unsigned int);
    ~FFTPool();

    unsigned int    getNumTaps() { return m_uNumTaps; } 
    bool            empty();
    bool            push(unsigned short*, unsigned int);
    void            setCallback(fftpool_callback_fptr);
    bool            setWindowFunction(FFT_REAL_TYPE*, unsigned int, unsigned int);
    bool            waitForEmpty();

    static void*    threadLoop(void*);



   

};



#endif // _FFTPOOL_H_