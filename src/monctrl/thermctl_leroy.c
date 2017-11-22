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
  temp_limit = 39.0;   

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
  usb = 0;
  while (usb >= 0 && usb < 3 && found == 0)
  {
    // Open a USB device
    sprintf(txt,"stty -F /dev/ttyUSB%d 9600 cs8 -cstopb -parity -icanon min 1 time 1 clocal",usb);
    printf("%s\n", txt);
    system(txt);
    usbdev=0;
    sprintf(txt,"/dev/ttyUSB%d",usb);
    usbdev = open(txt,O_RDWR);

    //-----------------------------------------------
    // loop over commands to execute
    //-----------------------------------------------
    outset=outbw=outgain=outvolt=set=tmp=pwr=gain=bw=deriv=volt=swvolt=enabled=0;
	for(mm=0;mm<68;mm++)
	{
      t=0; 
/*
      if(mm==0) {mode= 0x1c;t=25*100;}// set temperature point
      if(mm==1) {mode= 0x1d;t=3*100;}    // set bandwidth
      if(mm==2) {mode= 0x1e;t=0.3*100;}    // set integral gain
      //if(mm==3) {mode= 0x16;t=20*1000;}    // set voltage
      if(mm==4) mode= 0x03;         // read set point
      if(mm==5) mode= 0x01;         // read temp
      if(mm==6) mode= 0x04;         // read pwr
      if(mm==7) mode= 0x51;         // read bw
      if(mm==8) mode= 0x52;         // read gain
      if(mm==9) mode= 0x53;         // read deriv
      if(mm==10) mode= 0x46;         // read voltage
      if(mm==11) mode= 0x02;         // read switch voltage
//      if(mm==12) {mode = 0x1d; t=0;} // Disable active control
      if(mm==12) {mode = 0x2d; t=1;} // Enable active control
*/
	if(mm==0) {mode= 0x28;t=0;}// Write alarm type: 0 = no alarm, 1 = tracking alarm, 2 = fixed alarm, 3 = computer controlled alarm 
	if(mm==1) {mode= 0x29;t=5;}// Write Set type Define: 0= computer set value. 1= potentiometer input, 2= 0-5v input, 3= 0-20ma input,4= desire control 0x20 &0x21,5= JP3 Display 
	if(mm==2) {mode= 0x2a;t=1;}// Write sensor type: 0=5k,1=15K,2=10K,3=230K,4=50K,5=10K
	if(mm==3) {mode= 0x2b;t=1;}// Write control type: 0=deadband control,1=pid control,2=temp2 control
	if(mm==4) {mode= 0x2c;t=0;}// Write output polarity: 0=Heat wp1+ and wp2-,1= Heat wp2+ and wp1-
	if(mm==5) {mode= 0x2d;t=1;}// Write power on/off: 0=poweroff,1=poweron
	if(mm==6) {mode= 0x2e;t=0;}// Write  output shutdown if alarm: 0=no shutdown upon alarm,1=shutdown upon alarm
	if(mm==7) {mode= 0x1c;t=22*100;}// Write fixed desire control setting: set temperature has a multiplier of 100P: 25C = 25*100
	if(mm==8) {mode= 0x1d;t=3*100;}// Write proportional bandwidth: multiplier of 100 1deg=1*100
	if(mm==9) {mode= 0x1e;t=0.3*100;}// Write integral gain: repeats/min multiply by 100: 1 rep/min = 100*1
	if(mm==10) {mode= 0x1f;t=0*100;}// Write derivative gain: multiply by 100: 1min = 100*1
	if(mm==11) {mode= 0x20;t=0;}// Write Low external set range: 0v for input 2
	if(mm==12) {mode= 0x21;t=5;}// Write High external set range: 0-5v, 5v for input 2
/*	if(mm==13) {mode= 0x22;}// Write alarm deadband: leave blank for value t
	if(mm==14) {mode= 0x23;}// Write high alarm setting: leave blank for value t
	if(mm==15) {mode= 0x24;}// Write Low alarm setting: leave blank for value t
	if(mm==16) {mode= 0x25;}// Write control deadband setting: leave blank for value t
	if(mm==17) {mode= 0x26;}// Write input1 offset: value to offset input1 in order to calibrate external sensor if desired
	if(mm==18) {mode= 0x27;}// Write input2 offset: value to offset input2 in order to calibrate external sensor if desired
	if(mm==19) {mode= 0x0c;t=25*100;}// Write heat multiplier: multiply the heater percentage of power 100=1
	if(mm==20) {mode= 0x0d;t=25*100;}// Write cool multiplier:  multiply the cooling percentage of power 100=1
	if(mm==21) {mode= 0x0e;t=100;}// Write over current count compare value: current is roughly 2.5A/count
	if(mm==22) {mode= 0x2f;t=25*100;}// Write alarm latch enable: 0=lacthing enabled,1= lactching disabled, if alarm type=3 then 1=computer alarm on,0= computer alarm off 
	if(mm==23) {mode= 0x30;t=00;}// Write communication address: use 00 for universal value
	if(mm==24) {mode= 0x33;t=25*100;}// Write alarm latch reset: send to reset the alarms
	if(mm==25) {mode= 0x31;t=25*100;}// Write choose sensor for alarm function: 0=control sensor input, 1= input2 secondary input
	if(mm==26) {mode= 0x32;t=1;}// Write Choose C or F Temperature: 0=F,1=C
	if(mm==27) {mode= 0x34;t=1;}// Write EEPROM write enable or disable: 0= disable, 1= enable
	if(mm==28) {mode= 0x35;t=1;}// Write over current continuous: 1= continuous retry when over current is detected,0= allows the restart attempts value to be used
	if(mm==29) {mode= 0x0f;t=25*100;}// Write over current restart attemps: range from 0-30,000
	if(mm==30) {mode= 0x36;t=1;}// Write JP3 display enable: 0=disabled,1=enabled
*/
	if(mm==31) {mode= 0x01;}// Read  Serial commands:
	if(mm==32) {mode= 0x03;}// Read  Desired control value
	if(mm==33) {mode= 0x02;}// Read  power output:
	if(mm==34) {mode= 0x04;}// Read  power output %:
/*	if(mm==35) {mode= 0x05;}// Read  alarm status:
	if(mm==36) {mode= 0x06;}// Read  input2:
	if(mm==37) {mode= 0x07;}// Read  output current counts:
	if(mm==38) {mode= 0x41;}// Read  alarm type:
	if(mm==39) {mode= 0x42;}// Read  set type define:
	if(mm==40) {mode= 0x43;}// Read  sensor type:
	if(mm==41) {mode= 0x44;}// Read  control type:
*/
	if(mm==42) {mode= 0x45;}// Read  control output polarity:
	if(mm==43) {mode= 0x46;}// Read  power on/off:
	if(mm==44) {mode= 0x47;}// Read  output shutdown if alarm:
	if(mm==45) {mode= 0x50;}// Read  fixed desired control setting:
	if(mm==46) {mode= 0x51;}// Read  proportional bandwidth:
	if(mm==47) {mode= 0x52;}// Read  integral gain:
	if(mm==48) {mode= 0x53;}// Read  derivative gain:
/*	if(mm==49) {mode= 0x54;}// Read  low external set range:
	if(mm==50) {mode= 0x55;}// Read  high external set range:
	if(mm==51) {mode= 0x56;}// Read  alarm deadband:
	if(mm==52) {mode= 0x57;}// Read  high alarm setting:
	if(mm==53) {mode= 0x58;}// Read  low alarm setting:
	if(mm==54) {mode= 0x59;}// Read  control deadband setting:
	if(mm==55) {mode= 0x5a;}// Read  input1 offset:
	if(mm==56) {mode= 0x5b;}// Read  input2 offset:
	if(mm==57) {mode= 0x5c;}// Read  heat multiplier:
	if(mm==58) {mode= 0x5d;}// Read  cool multiplier:
	if(mm==59) {mode= 0x5e;}// Read  over current count compare value:
	if(mm==60) {mode= 0x48;}// Read  alarm latch enable:
	if(mm==61) {mode= 0x49;}// Read  communication address:
	if(mm==62) {mode= 0x4a;}// Read  choosen sensor for alarm function:
	if(mm==63) {mode= 0x4b;}// Read  choosen C or F temperature working units:
	if(mm==64) {mode= 0x4c;}// Read  eeprom write enable or disable:
	if(mm==65) {mode= 0x4d;}// Read  over current continuous:
	if(mm==66) {mode= 0x5f;}// Read  over current restart attemps:
	if(mm==67) {mode= 0x4e;}// Read  JP3 display enable:
*/
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
      printf("(etx=%x)\n",command[15]);

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

      /*printf("revcd from %02x = %d %f\n",mode,t,t/100.0);
      if (mm==45) fixed set control = t/100.0;
      if (mm==46) outbw = t/100.0;
      if (mm==47) outgain = t/100.0;
      if (mm==3) outvolt = t/1000.0;
      if (mm==32) desired set control = t/100.0;
      if (mm=33) power = t/100.0;
      if (mm=34) power % = t*100.0/683.0;
      if (mm==7) bw = t/100.0;
      if (mm==8) gain = t/100.0;
      if (mm==9) deriv = t/10.0;
      if (mm==10) volt = t/1000.0;
      if (mm==11) swvolt = t/1000.0;
      if (mm==12) enabled = t;
*/
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
    if ((file1 = fopen("/media/DATA/data/thermlog.txt", "a")) == NULL) 
    {
      if ((file1 = fopen("/media/DATA/data/thermlog.txt", "w")) == NULL) 
      {
        printf("cannot write %s\n", "/media/DATA/data/thermlog.txt");
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
    // And do it twice because sometime the first time doesn't communicate
    system("/media/DATA/codes/edges_c/power_switch8 -cmd 'gpset 1 0'");
    system("/media/DATA/codes/edges_c/power_switch8 -cmd 'gpset 1 0'");

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





