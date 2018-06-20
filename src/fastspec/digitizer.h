#ifndef _DIGITIZER_H_
#define _DIGITIZER_H_


#define digitizer_callback_fptr std::function<unsigned int(unsigned short*, unsigned int, unsigned long)>


// ---------------------------------------------------------------------------
//
// Digitizer
//
// Virtual Interface for digitizer classes
//
// ---------------------------------------------------------------------------
class Digitizer {

  public:

    virtual bool    acquire(unsigned long) = 0; 
    virtual bool    connect(unsigned int) = 0;
    virtual void    disconnect() = 0;
    virtual void    setCallback(digitizer_callback_fptr) = 0;
    virtual void    stop() = 0;

};



#endif // _DIGITIZER_H_
