#pragma once
#include <time.h>

void write_spec(double *, int, int);
void write_status(double *data, int argc, char **argv, time_t *starttime, int nrun, int nblock, int pport, int run, double duty_cycle);