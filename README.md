# ntp_client_python
An NTP client made using Python and C. Adjusts system clock based on offset.

## Configuration
Edit the config.ini to use the desired NTP server.

## Compile the .so
```bash
gcc -fPIC -shared -o adjtime_ntp.so adjtime_ntp.c
```
