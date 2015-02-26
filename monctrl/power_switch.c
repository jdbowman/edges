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


int main(int argc, char **argv)
{ int usbdev;
  int status,i,mode,m,usb;
  char command[16],resp[2560],buf[256],txt[256];

  mode = -1; usb = 0;
  for(m=0;m<argc;m++){
  sscanf(argv[m], "%79s", buf);
   if (strstr(buf, "-mode")) {sscanf(argv[m+1], "%d",&mode);}
   if (strstr(buf, "-usb")) {sscanf(argv[m+1], "%d",&usb);}
  }

 if(mode == -1) { printf("-mode 0 to turn off\n");
                  printf("-mode 1 to turn on\n");
                  printf("-mode 10 to get cmd list\n");
                  printf("-mode 3 to get status\n");
                  return 0;
                 }
  sprintf(txt,"stty -F /dev/ttyUSB%d 9600 cs8 -cstopb -parity -icanon min 1 time 1 clocal -echo",usb);
// needed -echo on temp4  - depends on verion of linux
  system(txt);
  usbdev=0;
  sprintf(txt,"/dev/ttyUSB%d",usb);
  usbdev = open(txt,O_RDWR);
//  printf("usbdev %x\n",usbdev);

  if(mode==10) sprintf(command,"?\n");
  else sprintf(command,"$A7 %d\n",mode);
  if(mode==3) sprintf(command,"$A5\n");

//  printf("%d chars\n",(int)strlen(command));
//  for (i=0;i<(int)strlen(command);i++) printf("i = %d %x = %1c\n",i,command[i],command[i]);
  status = 0;
  status = write(usbdev,command,strlen(command));
//  printf("status %d\n",status);
  sleep(3);
//  printf("start to read\n");
  status=0;
  for(i=0;i<2560;i++) resp[i]=0;
  status = read(usbdev,resp,2560);
//  printf("status = %d\n",status);
  for (i=0;i<status;i++) if(resp[i]) printf("%1c",resp[i]);
  close(usbdev);
  return 0;
}
