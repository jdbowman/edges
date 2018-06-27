#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sched.h>
#include <math.h>
#include <sys/io.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>

//-----------------------------------------------
// *** Thermal Control (thermctl) ***
//-----------------------------------------------


//-----------------------------------------------
// helper definitions
//-----------------------------------------------
double readclock (void);
void toyrday (double, int *, int *, int *, int *, int *);
double tosecs (int, int, int, int, int);
int turnoffpwr(int,int);


//-----------------------------------------------
// main
//
// user has to be root unless user is a member of dialout group
//
//-----------------------------------------------
int main(int argc, char **argv)
{ 
  int usbdev;
  int status,i,chk,t,j,chkrec,usb,mode,m,mm,yr,da,hr,mn,sc,found;
  double outset,outbw,outgain,outvolt,set,tmp,pwr,bw,gain,deriv,volt,swvolt,enabled,secs,temp_limit;
  char command[16],resp[12],buf[256],txt[256];
  FILE *file1;

  // Temperature for shut-down
  temp_limit = 45.0;   

  // Parse command line
  for (m=0; m<argc; m++)
  {
    sscanf(argv[m], "%79s", buf);
    if (strstr(buf, "-help")) 
    {
      printf("program monitors oven controller and kills power to EDGES if there is a problem\n");
      return 0; 
    }
    if (strstr(buf, "-temp_limit")) 
    {
       sscanf(argv[m + 1], "%lf", &temp_limit); 
       printf("setting temp_limit to %f\n",temp_limit);
    }  
  } // for

  //-----------------------------------------------
  // loop over USB ports until find the right one
  //-----------------------------------------------
  usb = found = 0;
  usb = 1;
  while (usb >= 0 && usb < 3 && found == 0)
  {
    // Open a USB device
    sprintf(txt,"stty -F /dev/ttyUSB%d 19200 cs8 -cstopb -parity -icanon min 1 time 1 clocal",usb);
    printf("%s\n", txt);
    system(txt);
    usbdev=0;
    sprintf(txt,"/dev/ttyUSB%d",usb);
    usbdev = open(txt,O_RDWR);

    //-----------------------------------------------
    // loop over commands to execute
    //-----------------------------------------------
    outset=outbw=outgain=outvolt=set=tmp=pwr=gain=bw=deriv=volt=swvolt=enabled=0;
    for(mm=0;mm<13;mm++)
    {
      t=0; 
      if(mm==0) {mode= 0x10;t=25*100;}// set temperature point
      if(mm==1) {mode= 0x11;t=3*100;}    // set bandwidth
      if(mm==2) {mode= 0x12;t=0.3*100;}    // set integral gain
      if(mm==3) {mode= 0x16;t=20*1000;}    // set voltage
      if(mm==4) mode= 0x40;         // read set point
      if(mm==5) mode= 0x01;         // read temp
      if(mm==6) mode= 0x04;         // read pwr
      if(mm==7) mode= 0x41;         // read bw
      if(mm==8) mode= 0x42;         // read gain
      if(mm==9) mode= 0x43;         // read deriv
      if(mm==10) mode= 0x46;         // read voltage
      if(mm==11) mode= 0x02;         // read switch voltage
//      if(mm==12) {mode = 0x1d; t=0;} // Disable active control
      if(mm==12) {mode = 0x1d; t=1;} // Enable active control


      sprintf(command,"*00%02x%08x",mode,t);

      chk=0; 
      for(i=0;i<12;i++) { 
        chk += command[i+1]; 
      }
      sprintf(&command[13],"%02x",(chk%256));
      command[15] = 0x0d;

      printf("Command: ");
      for (i=0;i<15;i++) { 
        printf("%1c",command[i]);
      }
      printf("( etx=%x)\n",command[15]);

      // Send command to controller
      status = 0;
      status = write(usbdev,command,16);
      printf("status %x\n",status);

      // Pause briefly
      sleep(1);

      // Read response from controller
      status=0;
      status = read(usbdev,resp,12);
      printf("status %x resp %s\n",status,resp);

      // Translate response
      t=0; j=1; 
      for(i=0;i<8;i++) 
      { 
        if(resp[8-i] <= '9') 
        {
          m = '0'; 
        } else {
          m = 'a' - 10; 
        }
        
        t += (resp[8-i]-m)*j; 
        j = j*16;
      }

      printf("revcd from %02x = %d %f\n",mode,t,t/100.0);
      if (mm==0) outset = t/100.0;
      if (mm==1) outbw = t/100.0;
      if (mm==2) outgain = t/100.0;
      if (mm==3) outvolt = t/1000.0;
      if (mm==4) set = t/100.0;
      if (mm==5) tmp = t/100.0;
      if (mm==6) pwr = t*100.0/683.0;
      if (mm==7) bw = t/100.0;
      if (mm==8) gain = t/100.0;
      if (mm==9) deriv = t/10.0;
      if (mm==10) volt = t/1000.0;
      if (mm==11) swvolt = t/1000.0;
      if (mm==12) enabled = t;

      chkrec=0; 
      for (i=0;i<8;i++) { 
        chkrec += resp[i+1]; 
      }

      t=0; j=1; 
      for (i=0;i<2;i++) {

        if (resp[10-i] <= '9') {
          m = '0'; 
        } else {
          m = 'a' - 10;
        }
        t += (resp[10-i]-m)*j; j = j*16;
      }

      if (t == (chkrec%256)) {
        found = 1;  // sucess found right device
      } else {
        printf("chk error %x %x\n",t,chkrec%256);
        usb++; // prepare to try next USB device
      }
    }

    // Close current USB device
    close(usbdev); 

    // Print status to terminal
    printf(" outset: %5.2f\n outbw: %5.2f\n outgain: %5.2f\n outvolt: %5.2f\n set: %5.2f\n temp: %5.2f\n pwr: %5.2f\n bandwidth: %5.2f\n gain: %5.2f\n deriv: %.2f\n voltage: %.2f\n switch voltage: %.2f\n enabled (always returns zero): %5.2f\n", outset, outbw, outgain, outvolt, set, tmp, pwr, bw, gain, deriv, volt, swvolt, enabled);
  


    //-----------------------------------------------
    // Save status to log file
    //-----------------------------------------------
    status = -1;
    if ((file1 = fopen("/home/loco/edges/data/thermlog_low2.txt", "a")) == NULL) 
    {
      if ((file1 = fopen("/home/loco/edges/data/thermlog_low2.txt", "w")) == NULL) 
      {
        printf("cannot write %s\n", "/home/loco/edges/data/thermlog_low2.txt");
        return 0;
      }
      status = 1;
    } else {
      status = 1;
    }

    if (status)
    {
      secs = readclock();
      toyrday(secs, &yr, &da, &hr, &mn, &sc);
      fprintf(file1, "%4d:%03d:%02d:%02d:%02d  temp_set %7.2f deg_C tmp %7.2f deg_C pwr %7.2f percent\n", yr, da, hr, mn, sc, set, tmp, pwr);
      fclose(file1);
    }

    // Pause briefly before trying the next USB port
    sleep(1);

  }  // while

  //-----------------------------------------------
  // Check the temperature cutoff
  //-----------------------------------------------
  if(tmp > temp_limit) {
    //if(usb == 1) turnoffpwr(0,0);  // pwr control must be 0
    //if(usb == 0) turnoffpwr(1,0);  // pwr control must be 1

    // Set outlet group #1 to off.  Outlet group #1 is configured in the switch 
    // to be the parts associated with the front-end (e.g. receiver and Oven Ind 
    // controller).
    //
    // And do it twice in case the first time doesn't communicate
    system("/home/loco/edges/src/py/powerOff.py");
    system("/home/loco/edges/src/py/powerOff.py");

  }

  return 0;
}


//-----------------------------------------------
// turnoffpwr
//-----------------------------------------------
int turnoffpwr(int usb,int mode)
{
  { int usbdev;
  int status,i,pwr;
  char command[16],resp[2560],txt[256];
  mode = 0; pwr = -99;
  sprintf(txt,"stty -F /dev/ttyUSB%d 9600 cs8 -cstopb -parity -icanon min 1 time 1 clocal -echo",usb);
  system(txt);
  usbdev=0;
  sprintf(txt,"/dev/ttyUSB%d",usb);
  usbdev = open(txt,O_RDWR);

  if(mode==10) sprintf(command,"?\n");
  else sprintf(command,"$A7 %d\n",mode);
  if(mode==3) sprintf(command,"$A5\n");

//  printf("%d chars\n",(int)strlen(command));
//  for (i=0;i<(int)strlen(command);i++) printf("%x = %1c ",command[i],command[i]);
  status = 0;
  status = write(usbdev,command,strlen(command));
//  printf("status %d\n",status);
  sleep(3);
  status=0;
  for(i=0;i<2560;i++) resp[i]=0;
  status = read(usbdev,resp,2560);
//  printf("status = %d\n",status);
  for (i=0;i<status;i++) printf("%1c",resp[i]);
  close(usbdev);
  pwr = resp[0] - 48;
  if(mode==0) printf("power turned off\n");
  return pwr;
  }
}



//-----------------------------------------------
// tosecs
//-----------------------------------------------
/* Convert to Seconds since New Year 1970 */
double tosecs(int yr, int day, int hr, int min, int sec)
{
    int i;
    double secs;
    secs = (yr - 1970) * 31536000.0 + (day - 1) * 86400.0 + hr * 3600.0 + min * 60.0 + sec;
    for (i = 1970; i < yr; i++) {
        if ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0)
            secs += 86400.0;
    }
    if (secs < 0.0)
        secs = 0.0;
    return secs;
}



//-----------------------------------------------
// readclock
//-----------------------------------------------
double readclock(void)
{
    time_t now;
    double secs;
    struct tm *t;
    now = time(NULL);
    t = gmtime(&now);
// gmtime Jan 1 is day 0
    secs = tosecs(t->tm_year + 1900, t->tm_yday + 1, t->tm_hour, t->tm_min, t->tm_sec);
    return (secs);
}


//-----------------------------------------------
// toyrday
//-----------------------------------------------
void toyrday(double secs, int *pyear, int *pday, int *phr, int *pmin, int *psec)
{
    double days, day, sec;
    int i;
    day = floor(secs / 86400.0);
    sec = secs - day * 86400.0;
    for (i = 1970; day > 365; i++) {
        days = ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) ? 366.0 : 365.0;
        day -= days;
    }
    *phr = sec / 3600.0;
    sec -= *phr * 3600.0;
    *pmin = sec / 60.0;
    *psec = sec - *pmin * 60;
    *pyear = i;
    day = day + 1;
    *pday = day;
    if (day == 366)             // fix for problem with day 366
    {
        days = ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) ? 366 : 365;
        if (days == 365) {
            day -= 365;
            *pday = day;
            *pyear = i + 1;
        }
    }
}





