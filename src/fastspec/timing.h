#ifndef _TIMING_H_
#define _TIMING_H_

#include <string>
#include <time.h>
#include <math.h>


// ---------------------------------------------------------------------------
//
// TIMER
//
// High-precision timer class (nanosecond)
//
// ---------------------------------------------------------------------------
class Timer {

  private:

    struct timespec     m_tic;
    double              m_dInterval;  // seconds
 
  public:

    // Constructor and destructor
    Timer() { 
      m_tic.tv_sec = 0; 
      m_tic.tv_nsec = 0; 
      m_dInterval = 0; 
    }

    ~Timer() {}

    // Public functions
    double get() { return m_dInterval; }

    void tic() { clock_gettime(CLOCK_MONOTONIC, &m_tic); } 

    double toc() { 

      struct timespec toc;
      clock_gettime(CLOCK_MONOTONIC, &toc); 
        
      // Calculate the difference between tic and toc in seconds
      m_dInterval = (toc.tv_sec - m_tic.tv_sec) + (toc.tv_nsec - m_tic.tv_nsec) / 1e9; 

      return m_dInterval;
    }

}; // Timer
  



// ---------------------------------------------------------------------------
//
// TIMEKEEPER
//
// Wrapper class for date-time storage and simple manipulation.  The principal
// storage unit is seconds since 00:00:00 January 1, 1970.
//
// ---------------------------------------------------------------------------
class TimeKeeper {
  
  private:

    // Member variables
    int    m_iYear;
    int    m_iDayOfYear;
    int    m_iHour;
    int    m_iMinutes;
    int    m_iSeconds;
    double          m_dSecondsSince1970;

  public:

    // Constructor and destructor
    TimeKeeper() : m_iYear(1970), m_iDayOfYear(1), 
                    m_iHour(0), m_iMinutes(0), m_iSeconds(0), 
                    m_dSecondsSince1970(0) { }
    
    ~TimeKeeper() { }


    // Public functions
    double set(double dSecondsSince1970) { 

      m_dSecondsSince1970 = dSecondsSince1970;
      getDateTimeFromSecondsSince1970(dSecondsSince1970, &m_iYear, &m_iDayOfYear, &m_iHour, &m_iMinutes, &m_iSeconds);

      return dSecondsSince1970;
    }


    double setNow() {

      double dSecondsSince1970;
      int year, day, hour, min, sec;
      struct tm *t;
      time_t tTime = time(NULL);
      t = gmtime (&tTime); // gmtime Jan 1 is day 0
      
      year = t->tm_year + 1900;
      day = t->tm_yday + 1;
      hour = t->tm_hour;
      min = t->tm_min;
      sec = t->tm_sec;

      dSecondsSince1970 = (year - 1970) * 31536000.0 + (day - 1) * 86400.0 + hour * 3600.0 + min * 60.0 + sec;

      for (int i = 1970; i < year; i++) {
        if ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) {
          dSecondsSince1970 += 86400.0;
        }
      }

      if (dSecondsSince1970 < 0.0) {
        dSecondsSince1970 = 0.0;
      }

      m_dSecondsSince1970 = dSecondsSince1970;
      getDateTimeFromSecondsSince1970(dSecondsSince1970, &m_iYear, &m_iDayOfYear, &m_iHour, &m_iMinutes, &m_iSeconds);

      return m_dSecondsSince1970;
    }

    int year() { return m_iYear;}
    
    int doy() { return m_iDayOfYear;}
    
    int hh() { return m_iHour;}

    int mm() { return m_iMinutes;}

    int ss() { return m_iSeconds;}

    double secondsSince1970() { return m_dSecondsSince1970; }

    static void getDateTimeFromSecondsSince1970(double secs, 
                                                int *pyear, int *pday, 
                                                int *phr, int *pmin, 
                                                int *psec) {
      
      double days, day, sec;
      int i;

      day = floor (secs / 86400.0);
      sec = secs - day * 86400.0;
      for (i = 1970; day > 365; i++) {      
        days = ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) ? 366.0 : 365.0;
        day -= days;
      }

      *phr = (int) (sec / 3600.0);
      sec -= *phr * 3600.0;
      *pmin = (int) (sec / 60.0);
      *psec = (int) (sec - *pmin * 60);
      *pyear = i;
      day = day + 1;
      *pday = (int) day;

      if (day == 366) {        // fix for problem with day 366
        days = ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) ? 366 : 365;
        if (days == 365) {
          day -= 365;
          *pday = (int)day;
          *pyear = i + 1;
        }
      }
    }

    static int getDayOfYearFromDate(int year, 
                                             int month, 
                                             int day) {
      int i, leap;
      int daytab[2][13] = {
                {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31},
                {0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31} };
      leap = (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
      for (i = 1; i < month; i++) {
        day += daytab[leap][i];
      }

      return (day);
    }

    std::string getFileString(int uLevel)
    {
      std::string sDateString;
      char txt[32];

      switch (uLevel) 
      {
      case 1:
        sprintf(txt, "%04d", m_iYear);
        break;
      case 2:
        sprintf(txt, "%04d_%03d", m_iYear, m_iDayOfYear);
        break;
      case 3:
        sprintf(txt, "%04d_%03d_%02d", m_iYear, m_iDayOfYear, m_iHour);
        break;
      case 4:
        sprintf(txt, "%04d_%03d_%02d_%02d", m_iYear, m_iDayOfYear, m_iHour, 
                m_iMinutes);
        break;
      default:
        sprintf(txt, "%04d_%03d_%02d_%02d_%02d", m_iYear, m_iDayOfYear, m_iHour, 
                m_iMinutes, m_iSeconds);
      }
      
      return std::string(txt);
    }

};


#endif // _TIMING_H_

