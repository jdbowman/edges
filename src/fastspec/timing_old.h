#ifndef _TIMING_H
#define _TIMING_H


#include <time.h>


/* Convert to seconds since New Year 1970 */
double tosecs (int yr, int day, int hr, int min, int sec)
{
  int i;
  double secs;

  secs = (yr - 1970) * 31536000.0 + (day - 1) * 86400.0 + hr * 3600.0 + min * 60.0 + sec;

  for (i = 1970; i < yr; i++)
  {
    if ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0)
    {
      secs += 86400.0;
    }
  }

  if (secs < 0.0)
  {
    secs = 0.0;
  }
  return secs;
}


/* Convert seconds since 1970 to Yr/Day/Hr/Min/Sec */
void toyrday (double secs, int *pyear, int *pday, int *phr, int *pmin, int *psec)
{
  double days, day, sec;
  int i;

  day = floor (secs / 86400.0);
  sec = secs - day * 86400.0;
  for (i = 1970; day > 365; i++)
  {      
    days = ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) ? 366.0 : 365.0;
    day -= days;
  }
  *phr = (int)(sec / 3600.0);
  sec -= *phr * 3600.0;
  *pmin = (int)(sec / 60.0);
  *psec = (int)(sec - *pmin * 60);
  *pyear = i;
  day = day + 1;
  *pday = (int)day;
  if (day == 366)         // fix for problem with day 366
  {
    days = ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) ? 366 : 365;
    if (days == 365)
    {
            day -= 365;
            *pday = (int)day;
            *pyear = i + 1;
    }
  }
}



int dayofyear (int year, int month, int day)
{
        int i, leap;
        int daytab[2][13] = {
                {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31},
                {0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}
        };
        leap = (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        for (i = 1; i < month; i++)
   {
                day += daytab[leap][i];
        }

        return (day);
}



double readclock (void)
{
  time_t now;
  double secs;
  struct tm *t;
  now = time (NULL);
  t = gmtime (&now); // gmtime Jan 1 is day 0
  secs = tosecs (t->tm_year + 1900, t->tm_yday + 1, t->tm_hour, t->tm_min, t->tm_sec);
  return secs;
}



#endif
