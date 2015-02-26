#include <stdio.h>
#include "fileio.h"
#include "datetime.h"
#include "d1typ6.h"

extern d1type d1;

char chFileACQ[1024] = "/disk1/edges/data/%4d_%03d_%02d.acq";
char chFileStatus[1024] = "/disk1/edges/data/status.txt";


// -----------------------------------------------
// Write Spectrum Line to ACQ file format         
// -----------------------------------------------
void write_spec(double data[], int num, int swpos)
{
	FILE *file1;
	int yr, da, hr, mn, sc, i,j,k;
	char txt[256];
	char b64[64];

	// Populate the encoding array
	for (i = 0; i < 26; i++) 
	{
		b64[i] = 'A' + i;
		b64[i + 26] = 'a' + i;
	}
	for (i = 0; i < 10; i++)
	{
        b64[i + 52] = '0' + i;
	}
	b64[62] = '+';
	b64[63] = '/';
	
	d1.secs = readclock();

	if(d1.foutstatus==0) 
	{
      toyrday (d1.secs, &yr, &da, &hr, &mn, &sc);
      d1.rday = da;
      sprintf (d1.filname, chFileACQ, yr, da, hr);
	}	

	// Open the output file for appending
	if ((file1 = fopen (d1.filname, "a")) == NULL)
	{
		if ((file1 = fopen (d1.filname, "w")) == NULL)
		{
			d1.foutstatus = -99;
			printf ("cannot write %s\n", d1.filname);
			return;
		}
		d1.foutstatus = 1;
	} 
	else 
	{
		d1.foutstatus = 1;
	}

	// Write to the file	
  	if (d1.foutstatus == 1)
  	{
  		toyrday (d1.secs, &yr, &da, &hr, &mn, &sc);
		if (da != d1.rday && swpos == 0)
		{
	  		fclose (file1);
	  		d1.foutstatus = 0;
	  		toyrday (d1.secs, &yr, &da, &hr, &mn, &sc);
	  		sprintf (d1.filname, chFileACQ, yr, da, hr);
	  		if ((file1 = fopen (d1.filname, "w")) == NULL)
	    	{
				d1.foutstatus = -99;
				return;
	    	}
	  		d1.foutstatus = 1;
		}

		// Write the ancillary information before the spectrum data
		fprintf (file1, "# swpos %d resolution %8.3f adcmax %8.5f adcmin %8.5f temp %2.0f C nblk %d nspec %d\n",
                        swpos,d1.fres,d1.adcmax,d1.adcmin,d1.temp,d1.numblk,d1.nspec);

		sprintf (txt, "%4d:%03d:%02d:%02d:%02d %1d %8.3f %8.6f %8.3f %4.1f spectrum ", 
						yr, da, hr, mn, sc, swpos, d1.fstart, d1.fstep, d1.fstop, d1.adcmax);
	   
		fprintf (file1, "%s", txt);

		// Encode the spectrum data and write it
		for(i=0; i<num; i++) 
		{
			k = -(int)(data[i] * 1e05);
			if(k > 16700000) 
			{
				k = 16700000;
			}

			if(k < 0) 
			{
				k = 0;	
			}

			for(j=0; j<4; j++) 
			{	
				txt[j] = b64[k >> (18-j*6) & 0x3f]; 
			}
			txt[4] = 0;
			fprintf(file1,"%s",txt);
		}

		fprintf (file1,"\n");
		fclose (file1);

		if(swpos == 0) 
		{
			d1.rday = da;
		}
	}
}



// -----------------------------------------------
// Write a status dump file                      
// -----------------------------------------------
void write_status(
         double *data,
         int argc, 
         char **argv, 
         time_t *starttime, 
         int nrun, 
         int nblock, 
         int pport, 
         int run, 
         double duty_cycle)
         
{

	FILE *file;
	char filename[1024];
	char buffer[2048];
	int n;
	time_t currenttime;
	struct tm timeinfo;
	// also inherits d1 from global context

	sprintf(filename, "%s", chFileStatus);
	if ((file = fopen(filename, "w")) == NULL)
	{
		printf ("Cannot write %s\n", d1.filname);
		return;
	}

	// Print current time
	time(&currenttime);
	gmtime_r(&currenttime, &timeinfo);
	strftime(buffer, 2048, "%c (UTC)", &timeinfo);
	fprintf(file, "Status: current time = %s\n", buffer);
	fprintf(file, "\n");

	// Print process command (e.g. "edges_spec -nspec 16384 -disp -")
	fprintf(file, "Process: command = ");
	for (n=0; n<argc; n++)
	{
		fprintf(file, "%s ", argv[n]);
	}
	fprintf(file, "\n");

	// Print process start time
	gmtime_r(starttime, &timeinfo);
	strftime(buffer, 2048, "%c (UTC)", &timeinfo);
	fprintf(file, "Process: start time = %s\n", buffer);
	fprintf(file, "\n");

	// Print current parameter values
	fprintf (file, "Parameter: nrun = %d\n", nrun);
	fprintf (file, "Parameter: nblock = %d\n", nblock);
	fprintf (file, "Parameter: pport = %d\n", pport);
	fprintf (file, "Parameter: run = %d\n", run);
	fprintf (file, "Parameter: duty_cycle = %6.3f\n", duty_cycle);
	fprintf (file, "Parameter: d1.mfreq = %6.3f\n", d1.mfreq);
	fprintf (file, "Parameter: d1.fres = %6.3f\n", d1.fres);
	fprintf (file, "Parameter: d1.temp = %6.3f\n", d1.temp);
	fprintf (file, "Parameter: d1.adcmin = %6.3f\n", d1.adcmin);
	fprintf (file, "Parameter: d1.adcmax = %6.3f\n", d1.adcmax);
	fprintf (file, "Parameter: d1.numblk = %d\n", d1.numblk);
	fprintf (file, "Parameter: d1.nspec = %d\n", d1.nspec);
	fprintf (file, "Parameter: d1.disp = %d\n", d1.disp);
	fprintf(file, "\n");

	// Print current spectra
	fprintf(file, "Data [freq (MHz), p0, p1, p2]:\n");
	for (n=0; n<d1.nspec; n++)
	{
		fprintf(file, "%8.3f, %8.3f, %8.3f, %8.3f\n", 
			(double) n * (d1.mfreq / (double) d1.nspec), 
			data[0*d1.nspec+n], 
			data[1*d1.nspec+n], 
			data[2*d1.nspec+n]);
	}
	fprintf(file, "\n");

	// That's all.  Close the file
	fclose(file);

}


