/*=================================================================
 *
 * decode.c     Decodes the EDGES raw spectrum into double.
 *
 *
 * This is a MEX-file for MATLAB.  
 *
 *=================================================================*/ 


#include "mex.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>



/* This makes a lookup table to convert an encoded char back into a
6-bit value */
static void initLookupTable(unsigned int* pLookupTable)
{
    int i = 0;
    for (i = 0; i<256; i++)
    {
        pLookupTable[i] = 0;
        if (i >= 'A' && i <= 'Z') {
            pLookupTable[i] = i - 'A';
        }
        if (i >= 'a' && i <= 'z') {
            pLookupTable[i] = i - 'a' + 26;
        }
        if (i >= '0' && i <= '9') {
            pLookupTable[i] = i - '0' + 52;
        }
        if (i == '+') {
            pLookupTable[i] = 62;
        }
        if (i == '/') {
            pLookupTable[i] = 63;
        }
    }
}


/* mexFunction is the gateway routine for the MEX-file */
void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
	bool bBadArgument = false;
	char* pEncoded = 0;
	int iEncodedLength = 0;
    double* pDecoded = 0;
    int iDecodedLength[2];
    unsigned int uLookupTable[256];
    int i = 0;

	/* Check the arguments */

	/* There should be 1 argument */
	if (nrhs != 1)
	{
		mexErrMsgTxt("Incorrect number of arguments (expected 1).");
		return;
	}

	/* Argument 1 should be the filename */
    if (mxGetClassID(prhs[0]) != mxCHAR_CLASS) bBadArgument = true;
	
	if (bBadArgument)
	{
		mexErrMsgTxt("One or more bad arguments.");
		return;
	}

	/* Get encoded spectrum */

	/* Allocate enough memory to hold the converted string. */
	iEncodedLength = mxGetNumberOfElements(prhs[0]);
	pEncoded = mxCalloc(iEncodedLength, sizeof(char));

	/* Copy the string data into the buffer */
	if (mxGetString(prhs[0], pEncoded, iEncodedLength + 1) != 0)
	{
        mexErrMsgTxt("Could not convert string data (EncodedSpectrum).");
	}
        
    /* Allocate the output arrays */
    iDecodedLength[0] = 1;
    iDecodedLength[1] = iEncodedLength / 4;
    plhs[0] = mxCreateNumericArray(2, iDecodedLength, mxDOUBLE_CLASS, mxREAL);
	pDecoded = (double*) mxGetData(plhs[0]);
       
    /* Initialize the lookup table */
    initLookupTable(uLookupTable);
    
    /* Decode the data */
    for (i=0; i<iDecodedLength[1]; i++)
    {
        int m = 4 * i;
        unsigned int temp = (uLookupTable[pEncoded[m]] << 18) + (uLookupTable[pEncoded[m+1]] << 12) + (uLookupTable[pEncoded[m+2]] << 6) + (uLookupTable[pEncoded[m+3]]);
        
        /* Put the spectrum into linear units (it was stored in dB*-1e5) */
        pDecoded[i] = pow((double) 10.0, (double) -0.1 * (double) temp * (double) 0.00001);
    
    }
    
    /* Free the input data copy */
    mxFree(pEncoded);
}



