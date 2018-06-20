
//#define FFT_SINGLE_PRECISION in Makefile
#define DEFAULT_INI_FILE "/home/loco/test.ini" //"/home/loco/edges.ini"

#define SIMULATE
#ifdef SIMULATE
  #include "pxsim.h"
  #define PX_DIGITIZER PXSim
  #define SWITCH SimulatedSwitch
#else
  #include "pxboard.h"
  #define PX_DIGITIZER PXBoard
  #define SWITCH ParallelPortSwitch
#endif

#include "ini.h"
#include "fftpool.h"
#include "spectrometer.h"
#include "switch.h"
#include "utility.h"
#include <functional>   // std::bind
#include <signal.h> // sigaction



// ----------------------------------------------------------------------------
// Global setup for handling SIGINT (Ctrl-c) signals 
// ----------------------------------------------------------------------------

static bool bStopSignal = false;

void on_signal(int iSignalNumber)
{
  printf("\n");
  printf("*** SIGINT received ***\n");
  printf("\n");
  printf("Program will exit at the conclusion of the switch cycle.\n");
  printf("\n");
  printf("This can be invoked by pressing CTRL-C in the execution\n");
  printf("terminal or by running the command 'kill -s SIGINT <PID>'\n");
  printf("with the appropriate processes ID <PID> from another\n");
  printf("terminal.\n");
  printf("\n");

  // Set the stop flag
  bStopSignal = true;
}

void register_signal() 
{
  // Change the signal action to use our onSignal() callback
  struct sigaction sAction;
  sAction.sa_handler = on_signal;
  sAction.sa_flags = SA_RESTART;
  sigemptyset(&sAction.sa_mask);
  sigaction(SIGINT,&sAction, NULL);
}



// ----------------------------------------------------------------------------
// print_help - Print help information to terminal
// ----------------------------------------------------------------------------
void print_help()
{
  printf("\n");
  printf("| ------------------------------------------------------------------------\n");
  printf("| EDGES Spectrometer\n");
  printf("| ------------------------------------------------------------------------\n");  
  printf("\n");
  printf("-f        Specify an output file.  If not specified, output files are\n");
  printf("          determined from the datadir parameter in the config file.\n");
  printf("\n");
  printf("-h        View this help message.\n");
  printf("\n");
  printf("-i        Specify the .ini configuration file.  If not specified, the\n");
  printf("          default configuration file is tried: \n\n");
  printf("               " DEFAULT_INI_FILE "\n");
  printf("\n");
  printf("stop      Send stop signal to any running spectrometer processes.\n");
  printf("\n");
}



// ----------------------------------------------------------------------------
// print_config - Print configuration to terminal
// ----------------------------------------------------------------------------
void print_config( const string& sConfigFile, const string& sSite, 
                   const string& sInstrument, const string& sOutput,
                   double dAcquisitionRate, double dBandwidth,
                   unsigned int uInputChannel, unsigned int uVoltageRange,
                   unsigned int uNumChannels, unsigned int uSamplesPerTransfer,
                   unsigned long uSamplesPerAccum, unsigned int uIOport,
                   unsigned int uNumFFT, unsigned int uNumThreads, 
                   unsigned int uNumBuffers, unsigned int uNumTaps)
{
  printf("\n");
  printf("| ------------------------------------------------------------------------\n");
  printf("| EDGES Spectrometer\n");
  printf("| ------------------------------------------------------------------------\n");  
  printf("| \n");
  printf("| Configuration file: %s\n", sConfigFile.c_str());
  printf("| \n");    
  printf("| Installation - Site: %s\n", sSite.c_str());
  printf("| Installation - Instrument: %s\n", sInstrument.c_str());
  printf("| Installation - Output path: %s\n", sOutput.c_str());
  printf("| \n");      
  printf("| Spectrometer - Digitizer - Input channel: %d\n", uInputChannel);
  printf("| Spectrometer - Digitizer - Voltage range mode: %d\n", uVoltageRange);
  printf("| Spectrometer - Digitizer - Number of channels: %d\n", uNumChannels);
  printf("| Spectrometer - Digitizer - Samples per transfer: %d\n", uSamplesPerTransfer);
  printf("| Spectrometer - Digitizer - Acquisition rate: %6.2f\n", dAcquisitionRate);
  printf("| Spectrometer - Digitizer - Samples per accumulation: %lu\n", uSamplesPerAccum);
  printf("| Spectrometer - Switch - Receiver switch IO port: 0x%x\n", uIOport); 
  printf("| Spectrometer - FFTPool - Number of FFT threads: %d\n", uNumThreads);
  printf("| Spectrometer - FFTPool - Number of FFT buffers: %d\n", uNumBuffers);
  printf("| Spectrometer - FFTPool - Number of window function taps: %d\n", uNumTaps);
  printf("| \n");  
  printf("| Bandwidth: %6.2f\n", dBandwidth);        
  printf("| Samples per FFT: %d\n", uNumFFT);    
  printf("| \n");              
  printf("| ------------------------------------------------------------------------\n"); 
  printf("\n");
}




// ----------------------------------------------------------------------------
// Main
// ----------------------------------------------------------------------------
int main(int argc, char* argv[])
{

    using namespace std::placeholders; // for std::bind arguments _1, _2, _3
    
    string sConfigFile(DEFAULT_INI_FILE);
    string sOutput;
    bool bDirectory = true;

    setbuf(stdout, NULL);

    // -----------------------------------------------------------------------
    // Parse the command line 
    // -----------------------------------------------------------------------
    for(int i=0; i<argc; i++)
    {
      string sArg = argv[i];

      if (sArg.compare("-i") == 0) { 
        if (argc > i) sConfigFile = argv[i+1]; 

      } else if (sArg.compare("-f") == 0) { 
        // Specify an output file instead of the usual directory structure
        if (argc > i) sOutput = argv[i+1]; 
        bDirectory = false;
      } else if (sArg.compare("-h") == 0) { 
        print_help();
        return 0;
      } else if (sArg.compare("stop") == 0) { 

      }
    }

    // -----------------------------------------------------------------------
    // Parse the Spectrometer configuration .ini file
    // -----------------------------------------------------------------------
    INIReader reader(sConfigFile);

    if (reader.ParseError() < 0) {
      printf("Failed to parse .ini config file.  Abort.\n");
      return 1;
    }

    string sDataDir = reader.Get("Installation", "datadir", "");
    string sSite = reader.Get("Installation", "site", "");
    string sInstrument = reader.Get("Installation", "instrument", "");
    unsigned int uIOport = reader.GetInteger("Spectrometer", "io_port", 0x3010);
    unsigned int uInputChannel = reader.GetInteger("Spectrometer", "input_channel", 2);
    unsigned int uNumChannels = reader.GetInteger("Spectrometer", "num_channels", 65536);
    unsigned long uSamplesPerAccum = reader.GetInteger("Spectrometer", "samples_per_accumulation", 200*2*1024*1024);
    unsigned int uSamplesPerTransfer = reader.GetInteger("Spectrometer", "samples_per_transfer", 2*1024*1024);
    unsigned int uVoltageRange = reader.GetInteger("Spectrometer", "voltage_range", 0);
    double dAcquisitionRate = reader.GetReal("Spectrometer", "acquisition_rate", 400);
    unsigned int uNumThreads = reader.GetInteger("Spectrometer", "num_fft_threads", 4);
    unsigned int uNumBuffers = reader.GetInteger("Spectrometer", "num_fft_buffers", 1000);
    unsigned int uNumTaps = reader.GetInteger("Spectrometer", "num_taps", 1);

    // Calculate a few derived configuration parameters
    double dBandwidth = dAcquisitionRate / 2.0;
    unsigned int uNumFFT = uNumChannels * 2;
    if (bDirectory) { 
      sOutput = sDataDir; 
    }

    // -----------------------------------------------------------------------
    // Print the configuration to terminal
    // ----------------------------------------------------------------------- 
    print_config( sConfigFile, sSite, sInstrument, sOutput, dAcquisitionRate, 
                  dBandwidth, uInputChannel, uVoltageRange, uNumChannels, 
                  uSamplesPerTransfer, uSamplesPerAccum, uIOport, uNumFFT, 
                  uNumThreads, uNumBuffers, uNumTaps );

    // -----------------------------------------------------------------------
    // Check the configuration
    // -----------------------------------------------------------------------  
    if (uSamplesPerTransfer % uNumFFT != 0) {
      printf("Warning: The number of samples per transfer is not a multiple "
             "of the number of FFT samples.  Will not be able to achieve "
             "100%% duty cycle.\n\n");
    }

    if (uSamplesPerAccum % uNumFFT != 0) {
      printf("Warning: The number of samples per accumulation is not a "
             "multiple of the number of FFT samples.\n\n");
    }

    // -----------------------------------------------------------------------
    // Register our override of ctrl-c and kill -s SIGINT. The global 
    // variable bStopSignal will turn true when an interrupt is received.
    // -----------------------------------------------------------------------
    register_signal();

    // -----------------------------------------------------------------------
    // Initialize the receiver switch
    // -----------------------------------------------------------------------   
    SWITCH sw; 
    if (!sw.init(uIOport)) {
      printf("Failed to control parallel port.  Abort.\n");
      return 1;
    }
    sw.set(0);

    // -----------------------------------------------------------------------
    // Initialize the digitizer board
    // -----------------------------------------------------------------------       
    PX_DIGITIZER px;
    px.setInputChannel(uInputChannel);
    px.setVoltageRange(1, uVoltageRange);
    px.setVoltageRange(2, uVoltageRange);
    px.setAcquisitionRate(dAcquisitionRate);
    px.setTransferSamples(uSamplesPerTransfer); // should be a multiple of number of FFT samples

    // Connect to the digitizer board
    if (!px.connect(1)) { 
      printf("Failed to connect to PX board. Abort. \n");
      return 1;
    }

    // -----------------------------------------------------------------------
    // Initialize the FFT pool
    // -----------------------------------------------------------------------
    FFTPool fft ( uNumThreads,
                  uNumBuffers,
                  uNumChannels );

    // Set the window function
    FFT_REAL_TYPE* pWindow = (FFT_REAL_TYPE*) malloc(uNumFFT*sizeof(FFT_REAL_TYPE));
    get_blackman_harris(pWindow, uNumFFT);
    fft.setWindowFunction(pWindow, uNumFFT, uNumTaps);

    free(pWindow);

    // -----------------------------------------------------------------------
    // Initialize the Spectrometer
    // -----------------------------------------------------------------------
    Spectrometer spec( uNumChannels, 
                       uSamplesPerAccum, 
                       dBandwidth, 
                       (Digitizer*) &px,
                       &fft,
                       &sw, 
                       &bStopSignal );

    spec.setOutput(sOutput, bDirectory);

    // -----------------------------------------------------------------------
    // Take data until a SIGINT is received
    // -----------------------------------------------------------------------    
    spec.run();

    return 0;
}