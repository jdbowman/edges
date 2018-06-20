#ifndef _SWITCH_H
#define _SWITCH_H

#include <stdio.h>
#include <sys/io.h> // ioperm, etc.
#include <unistd.h> // usleep

using namespace std;

#define SWITCH_SLEEP_MICROSECONDS 500000

class Switch {

public: 

    virtual unsigned int set(unsigned int) = 0;
    virtual unsigned int increment() = 0;
    virtual unsigned int get() = 0;

};



class ParallelPortSwitch : public Switch {

  private:

    // Member variables
    unsigned int    m_uIOport;
    unsigned int    m_uSwitchState;

  public:

    // Constructor and destructor
    ParallelPortSwitch() : m_uIOport(0), m_uSwitchState(0) {}
    ~ParallelPortSwitch() {}

    bool init(unsigned int uIOport) {
      // Define the base address of the Parallel port PCIe Card
      // Use command: lspci -v to find the first I/O port hex address
      // Use command: sudo modprobe parport_pc io=0x#### irq=## to update the kernal
      // module

      // Remember the port
      m_uIOport = uIOport;

      // Set the port access bits for this thread
      if (ioperm(m_uIOport, 3, 1) != 0) {
        printf("You must run this program with root privileges to access the parallel port.\n");
        return false;
      }

      return true;
    }


    unsigned int set(unsigned int uSwitchState) {

      int iWriteValue;
      if (uSwitchState == 0) iWriteValue = 0;  // antenna
      if (uSwitchState == 1) iWriteValue = 2;  // load
      if (uSwitchState == 2) iWriteValue = 3;  // load + cal

//printf("switch: read IO before outb = %d\n", inb(m_uIOport));

      // Send the switch state to the parallel port
      outb(iWriteValue, m_uIOport); 

//printf("switch: read IO after outb = %d\n", inb(m_uIOport));

      // Wait briefly (~0.1 sec) for it take effect
      usleep(SWITCH_SLEEP_MICROSECONDS); 

      // Remember the switch state
      m_uSwitchState = uSwitchState;

      return uSwitchState;
    }


    unsigned int increment() {
      return set((m_uSwitchState + 1) % 3);
    }


    unsigned int get() { return m_uSwitchState; }

};



class SimulatedSwitch : public Switch {

  private:

    unsigned int m_uSwitchState;

  public:

    // Constructor and destructor
    SimulatedSwitch() { m_uSwitchState = 0; printf("Using SIMULATED switch\n"); }
    ~SimulatedSwitch() {}

    bool init(unsigned int) { return true; }

    unsigned int set(unsigned int uSwitchState) {
      m_uSwitchState = uSwitchState;
      usleep(SWITCH_SLEEP_MICROSECONDS); 
      return uSwitchState;
    }

    unsigned int increment() {
      return set((m_uSwitchState + 1) % 3);
    }

    unsigned int get() { return m_uSwitchState; }

};




#endif
