#!/usr/bin/python
import os
import subprocess
import configparser
import logging
import ntplib
import ctypes
import errno


'''
Given an NTP Client and server host will make num_requests NTP requests and returns the most accurate offset.
'''
def get_offset(client: ntplib.NTPClient, ntp_host: str, port: int=123, num_requests: int=8, timeout: int=5):
    delay = float("inf")
    offset = 0
    for i in range(num_requests):
        # Get an ntplib.NTPStats object
        logging.debug("making NTP request #{} to: {}".format(i + 1, ntp_host))
        response = client.request(ntp_host, port=port, timeout=timeout)
        if delay > response.delay:
            logging.info("new delay {}s".format(response.delay))
            delay = response.delay
            offset = response.offset
    return offset

'''
Parse config file for logging level
'''
def get_log_level(config):
    log_level = config['log_level']
    log_level_dict = {'notset': logging.NOTSET,
                      'debug': logging.DEBUG,
                      'info': logging.INFO,
                      'warning': logging.WARNING,
                      'error': logging.ERROR,
                      'critical': logging.CRITICAL}
    return log_level_dict[log_level]
    

'''
Call the C so that runs adjtime.
'''
def adjtime_c(time_s: int, time_us: int, so_filepath: str):
    logging.debug("Calling C function from: {}".format(so_filepath))
    c_functions = ctypes.CDLL(so_filepath, use_errno=True)
    ret_val = c_functions.ntp_adjtime(time_s, time_us)
    err = ctypes.get_errno()
    if ret_val:
        logging.error("adjtime returned {}".format(ret_val))
        logging.critical(os.strerror(err))
        return
    logging.info("System clock is adjusting. This will run in the background.")
    return

'''
Call the OS date command to bring the time closer to speed up
the adjtime call.
'''
def adjust_date(offset: float):
    subprocess.run(["date", "-s", "{} seconds".format(offset)])
    return


if __name__ == "__main__":
    # Open config file
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Setup logging
    #logger = logging.getLogger(__name__)
    log_format = "[%(levelname)s: %(funcName)s] %(message)s"
    log_config = config['Logging']
    if log_config['log_file']:
        logging.basicConfig(filename=log_config['log_file'], level=get_log_level(log_config), format=log_format)
    logging.basicConfig(level=get_log_level(log_config), format=log_format)
    if log_config['enable_log'] != 'True':
        logging.disable(logging.CRITICAL)



    ntp_config = config['NTPSettings']
    # Create an NTPClient
    c = ntplib.NTPClient()

    # Calculate the offset from the NTP server
    offset = get_offset(c, ntp_config['ntp_url'], int(ntp_config['ntp_port']),
                        int(ntp_config['number_requests']), int(ntp_config['timeout_s']))

    # If we are really far off, adjust quickly and then use adjtime.
    if (abs(offset) > 1):
        adjust_date(offset)
        offset = get_offset(c, ntp_config['ntp_url'], int(ntp_config['ntp_port']),
                            int(ntp_config['number_requests']), int(ntp_config['timeout_s']))
        
    logging.info("Best offset calculated: {}".format(offset))
    seconds = int(offset)
    microseconds = int((offset - seconds)*1e+6)
    logging.debug("Seconds: {}".format(seconds))
    logging.debug("Microseconds: {}".format(microseconds))

    so_file = ntp_config['adjtime_so_path']
    adjtime_c(seconds, microseconds, so_file)
    
