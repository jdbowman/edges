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

//-----------------------------------------------
// *** Power Switch ***
//-----------------------------------------------

//-----------------------------------------------
// main
//-----------------------------------------------

int main(int argc, char **argv)
{ 
  int usbdev;
  int status,i,mode,m,usb;
  char command[16],resp[2560],buf[256],txt[256],cmd[256];

  mode = -1; usb = 0;
  for(m=1;m<argc;m++){
    sscanf(argv[m], "%79s", buf);
    if (strstr(buf, "-mode")) {
      sscanf(argv[++m], "%d", &mode);
    } else if (strstr(buf, "-usb")) {
      sscanf(argv[++m], "%d", &usb);
    } else if (strstr(buf, "-cmd")) {
      strcpy(cmd, argv[++m]);
      mode=-2;
    } 
  }

  if(mode == -1) { 
    printf("Usage: power_switch -cmd \"command arg1 arg2\"\n");
    printf("Example to get cmd list: power_switch -cmd ?\n");
    printf("Legacy support:\n");
    printf("-mode 0 to turn all off\n");
    printf("-mode 1 to turn all on\n");
    printf("-mode 10 to get cmd list\n");
    printf("-mode 3 to get status\n");
    return 0;
  }

//-----------------------------------------------
// Open the serial connection through USB
//-----------------------------------------------

  // Apply the settings of the serial terminal
  // Note: needed -echo -- depends on verion of linux
  sprintf(txt,"stty -F /dev/ttyUSB%d 9600 cs8 -cstopb -parity -icanon min 1 time 1 clocal -echo",usb);
  system(txt);

  // Open the connection
  sprintf(txt,"/dev/ttyUSB%d",usb);
  usbdev=0;
  usbdev = open(txt,O_RDWR);


//-----------------------------------------------
// Perform requested command
//-----------------------------------------------

  // Set the command to send 
  if(mode==10) {
    sprintf(command,"?\n");
  } else if (mode==0 || mode ==1) {
    sprintf(command,"$A7 %d\n",mode);
  } else if (mode==3) {
    sprintf(command,"$A5\n");
  } else if (mode<=-2) {
    sprintf(command, "%s\n", cmd);
  }

  // Send the command
  status = 0;
  status = write(usbdev,command,strlen(command));
  //printf("command status %d\n",status);

  // Pause briefly
  sleep(3);

  // Read the response
  status=0;
  for(i=0;i<2560;i++) resp[i]=0;
  status = read(usbdev,resp,2560);
  //printf("response status = %d\n",status);

  // Print the response
  for (i=0;i<status;i++) if(resp[i]) printf("%1c",resp[i]);

  // Close the connection
  close(usbdev);

  return 0;
}
