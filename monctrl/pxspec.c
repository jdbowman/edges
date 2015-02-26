//#include <gtk/gtk.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sched.h>
#include <fcntl.h>
#include <pthread.h>
#include <errno.h>
#include <signal.h>
#include <fftw3.h>
#include "d1typ6.h"
//#include "d1proto6.h"
#include "stdafx.h"
#include "fileio.h"
#include "datetime.h"
#include "parallelport.h"
#include "thermalcontroller.h"
#include "labjack_edges.h"

#define NSIZ 65536
#define MY_PX14400_BRD_NUM 1

//GdkPixmap *pixmap = NULL;
//GdkFont *fixed_font;
//GtkWidget *table;
//GtkWidget *button_exit;
//GtkWidget *drawing_area;
float avspec[NSIZ];
float win0[NSIZ*2],win1[NSIZ*2];
float win2[NSIZ*2],win3[NSIZ*2];
float spec0[NSIZ],spec1[NSIZ];
float spec2[NSIZ],spec3[NSIZ];
//int midx, midy;
HPX14 hBrd;
px14_sample_t *dma_bufp;
fftwf_plan p0,p1,p2,p3;
float *reamin0,*reamin1,*reamin2,*reamin3,*reamout0,*reamout1,*reamout2,*reamout3;
d1type d1;


void *runspec(void *);
void px14run(float*,int);
int pxrun(int,px14_sample_t *);


static void handler(int signum) 
{
	printf("SIG %d received\n", signum);
	printf("program will end at the end of the 3-pos cycle\n");
	printf("to terminate gracefully from kill use kill -s SIGINT\n");
	d1.run = 0;
}



// -------------------------------------------------------
// ----------------------- Main --------------------------
// -------------------------------------------------------
int main(int argc, char **argv)
{
	// ----------------------------
	// BEGIN PARAMETER DECLARATIONS
	static double data[3*NSIZ];
	static float spec[NSIZ];
	double max;
	int i,kk,maxi,run,nspec,nrun,nblock,pport;
	double av,freq,aa;
	int swmode, swmnext;
	char buf[256];
	struct sigaction sa;
	
	// -- duty cycle
	struct timespec tic, toc;
	double n_samples, n_seconds, duty_cycle;
	time_t starttime;
	
	// -- thermal controller
	int tc_device;
	double tc_setTemperature, tc_actualTemperature, tc_power;
	
	//-- weather station
	double weather_rackTemperature, weather_temperature, weather_humidity;
	double core_temp1, core_temp2, core_temp3, core_temp4;
	
	// END PARAMETER DECLARATIONS
	// --------------------------
  
	// Record the date that the process started
	time(&starttime);
	
	// Setup the kill -s event handler that aborts the process cleanly
	sa.sa_handler = handler;
	sigemptyset(&sa.sa_mask);
	sa.sa_flags = SA_RESTART;
	if (sigaction(SIGINT,&sa, NULL) == -1) 
	{
		printf("handler error\n");
	}

	// Set default parameter values
	nrun = 100000000; 
	nblock = 1280; // 160;
	pport = 1;
	d1.mfreq = 200.0; 
	d1.temp = 0; 
	d1.disp = 1; 
	d1.sim = 0;  
	d1.printout = 1; 
	d1.nspec = 32768;
	d1.dwin = 1;
	d1.dwin = 0;
	d1.run = 1;

	// Parse input arguments to update default values for this instance
	for(i=0; i<argc-1; i++)
	{
		sscanf(argv[i], "%79s", buf);
		if (strstr(buf, "-disp")) { sscanf(argv[i+1], "%d",&d1.disp); }
		if (strstr(buf, "-sim")) { sscanf(argv[i+1], "%d",&d1.sim); }
		if (strstr(buf, "-print")) { sscanf(argv[i+1], "%d",&d1.printout); }
		if (strstr(buf, "-nrun")) { sscanf(argv[i+1], "%d",&nrun); }
		if (strstr(buf, "-nblock")) { sscanf(argv[i+1], "%d",&nblock); }
		if (strstr(buf, "-nspec")) { sscanf(argv[i+1], "%d",&d1.nspec); }
		if (strstr(buf, "-pport")) { sscanf(argv[i+1], "%d",&pport); }
		if (strstr(buf, "-dwin")) { sscanf(argv[i+1], "%d",&d1.dwin); }
		if (strstr(buf, "-mfreq")) { sscanf(argv[i+1], "%lf",&d1.mfreq); }
	}

	// Start the Labjack connection for the weather station
	printf("Opening labjack USB connection for weather station\n");
    labjack_open(); 
	
	// Start the thermal controller connection
	printf("Opening thermal controller USB-to-serial connection\n");
	tc_device = thermalcontroller_open(thermalcontroller_findusb());
	thermalcontroller_readall(tc_device, &tc_setTemperature, &tc_actualTemperature, &tc_power);
	
	// Clear the parallel port data prior to commanding switch
	printf("Initializing the parallel port\n");
	if (pport)  
	{
		parport(-1);
	}

	// Set the user and group IDs from the current running instance (?)
	setgid(getgid());
	setuid(getuid());

	// Allow time for PCI bus to get ready
	printf("Waiting briefly for PCI bus to get ready\n");
	sleep(3);    
	

	//if (d1.disp)
	//{
	//	gtk_init(&argc, &argv);
	//	disp();
	//}

	d1.stim = 1e-6/(2.0*d1.mfreq);
	nspec = d1.nspec;
	d1.fstart = 0.0; 
	d1.fstop = d1.mfreq; 
	d1.fstep = d1.mfreq/nspec; 
	d1.fres = 4.0 * d1.mfreq * 1e03 / ((double)nspec);  
	d1.foutstatus = 0;
	run = 1; 
	
	// Initialize the spectrometer
	printf("Initializing the spectrometer\n");
	px14run(spec,-1);   // init

	if(pport)
	{
		printf("Sending switch command over parallel port\n");
		parport(0);  // set to antenna 
	}

	// The main running loop
	printf("Starting the main loop\n");
	while(run<=nrun && d1.run)
	{
		// The signatec card has a self-calibration function.
		// It may be useful to use this function from time to time.
		// Recalibrates every 120 cycles.
		//if (run > 1 && (run % 120) == 1) 
		//{
		//	printf("Acquiring spectrum\n");
		//	px14run(spec,-2); 
    	//}

		// Cycle through each of the switch states
    	for(swmode=0; swmode<3; swmode++) 
		{
			// Keep track of the start time for each switch state loop so
			// we can calcute effective duty cycle at the end of the loop.
			clock_gettime(CLOCK_MONOTONIC, &tic);

			// Reset parameters
			d1.adcmax = -1e99;
			d1.adcmin = 1e99;
			d1.mode = swmode;
			d1.numblk = 0;
			
			// Acquire new spectrum
			printf("Acquiring spectrum (nblock: %d)\n", nblock);
			px14run(spec, nblock);
	
			if (swmode == 2) 
			{
				swmnext = 0;
			} else {
				swmnext = swmode + 1;
			}
        
			// Set switch for next cycle as it needs acquire to set
			if(pport) 
			{
				printf("Sending switch command over parallel port\n");
				parport(swmnext); 
			}
        
			for(kk=0; kk<nspec; kk++) 
			{
				data[swmode*nspec+kk] = spec[kk];
			}
	
			// If the display flag was set at run, then draw the spectrum
			// to a gtk window on the screen.
			// if (d1.disp)
			// {
        		// aa = 100.0 / ((double) d1.numblk*nspec*2.0);  // for compatibility with acml FFT 
				// for(kk=0;kk<nspec;kk++) 
				// {
					// avspec[kk]=10.0*log10(aa*spec[kk]+1e-99);
				// }

				// d1.totp = 0.0;
				// for(kk=(int)(80.0*nspec/210.0);kk<nspec;kk++) 
				// {
					// d1.totp += spec[kk];
				// }

				// d1.secs = readclock();
				// Repaint(d1.mfreq);
				// while (gtk_events_pending()) 
				// {
					// gtk_main_iteration();
				// }
				// clearpaint();
			// } 

			max = -1e99;
			maxi = 0;
			aa = 1.0/((double)d1.numblk*nspec*2.0);  // for compatibility with acml FFT 

			for(kk=0;kk<nspec;kk++)
			{
        		av = aa * data[swmode*nspec+kk];
        		av = 10.0*log10(av) - 38.3;   // power in dBm -20 dBm into dp310 = -30 dbm
				if(kk < 10) 
				{
					av = -199.0;
				}
        		if(av > max)
				{ 
					max = av; 
					maxi=kk; 
				}
	        	data[swmode*nspec+kk]=av;
			}

			freq = d1.fstart + maxi*d1.mfreq/nspec;

			if (d1.printout) 
			{
				printf("max %f dBm maxkk %d swmode %d freq %5.1f MHz adcmax %8.5f %d adcmin %8.5f temp %2.0f C\n",
                max,maxi,swmode,freq,d1.adcmax,d1.maxindex,d1.adcmin,d1.temp);
			}
			
			// Calculate the effective duty cycle
			clock_gettime(CLOCK_MONOTONIC, &toc);
  			n_seconds = (toc.tv_sec - tic.tv_sec) + (toc.tv_nsec - tic.tv_nsec) / 1000000000.0;
			n_samples = (double) d1.numblk * (double) nspec;
			duty_cycle = 100.0 * n_samples / (d1.mfreq * 1e6) / n_seconds;
			printf("Duty cycle: %5.2f, duration: %5.2f, samples read: %5.2f, numblk: %d\n", 
				duty_cycle, n_seconds, n_samples, d1.numblk);

			// Write spectrum to output file
			write_spec(&data[swmode*nspec],nspec,swmode);

		} // end switch cycle for-loop

		// Read the weather station temperature and humidity
		labjack_readWeather(&weather_rackTemperature, &weather_temperature, &weather_humidity);
		printf("Weather station -- Rack temperature: %5.2f [C]\n", weather_rackTemperature);
		printf("Weather station -- Temperature: %5.2f [C]\n", weather_temperature);
		printf("Weather station -- Humidity: %5.2f\n", weather_humidity);

		// Read the CPU core temperatures
		coretemp_read(&core_temp1, &core_temp2, &core_temp3, &core_temp4);
		//printf("CPU core temperatures -- core 1: %5.2f, core 2: %5.2f, core 3: %5.2f, core 4: %5.2f\n", core_temp1, core_temp2, core_temp2, core_temp3, core_temp4);
		
		// Read the thermal controller temperature
		thermalcontroller_readall(tc_device, &tc_setTemperature, &tc_actualTemperature, &tc_power);
		printf("Thermal controller -- Set temperature: %5.2f [C]\n", tc_setTemperature);
		printf("Thermal controller -- Actual temperature: %5.2f [C]\n", tc_actualTemperature);
		printf("Thermal controller -- Actual power usage: %5.2f\n", tc_power);

		// Write to the status file
		clock_gettime(CLOCK_MONOTONIC, &tic);
		write_status(data, argc, argv, &starttime, nrun, nblock, pport, run, duty_cycle);
		clock_gettime(CLOCK_MONOTONIC, &toc);
		printf("Write status file - duration (seconds): %15f\n", 
        (toc.tv_sec - tic.tv_sec) + (toc.tv_nsec - tic.tv_nsec) / 1000000000.0 );

		// Increment the loop counter
		run++;

	} // end main while-loop

	// clean-up PCI
	px14run(spec,-3);  
	
	// clean-up the weather station labjack
	labjack_close();
	
	// clean-up the thermal controller
	thermalcontroller_close(tc_device);

	return 0;
}



