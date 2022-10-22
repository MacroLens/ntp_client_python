#ifndef NTP_ADJTIME
#define NTP_ADJTIME
#include <stddef.h>
#include <sys/time.h>

/*
 * This is compiled as a .so
 * Example:
 * gcc -fPIC -shared -o adjtime_ntp.so adjtime_ntp.c
 * 
 */


int ntp_adjtime(int seconds, int u_seconds) {
  struct timeval time;
  time.tv_sec = seconds;
  time.tv_usec = u_seconds;
  return adjtime(&time, NULL);
}

#endif
