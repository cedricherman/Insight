# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 13:02:21 2018

@author: herma
"""

import os
import argparse
from datetime import datetime, timedelta

def get_timeout(basedir, filename):
    """
    Retrieve inactivity period (aka timeout) from text file
    Text file must be located in input folder of root directory
    PARAMETERS
    basedir: current script directory
    filename: filename (.txt)
    Returns a timedelta object
    """
    full_path = os.path.join(basedir, os.pardir, 'input', filename)
    
    # check for file existence and extension
    is_valid_file(full_path, '.txt')
    
    # read first line
    with open(full_path) as f:
        timeout_string = f.readline()
    
    # check that casting to integer  works
    try:
        timeout = int(timeout_string)
    except:
        raise ValueError('Invalid Inactivity period. '
                         'Inactivity period must be an Integer')
        
    # check if timeout is in the right range
    if timeout < 1: 
        raise ValueError('Invalid Inactivity period. '
                         'Inactivity period must be at least 1 second')
    elif timeout > 86400:
        raise ValueError('Invalid Inactivity period. '
                         'Inactivity period cannot be greater than 86,400 seconds (24h)')
    
    return timedelta(seconds = timeout)

def extract_header(fp, header_list):
    """
    Record indexes based on field of interest
    PAREMETERS
    fp: file pointer
    header_list : list of field of interest (each field is a string)
    Returns a python dictionary with field->index mapping
    """
    # get header as string
    header_str = fp.readline()
    # remove trailing newline character and separate by comma
    header = header_str.rstrip('\n').split(',')
    # compute indexes for fields of interest
    try:
        indexes = { h : header.index(h) for h in header_list}
    except ValueError as verr:
        verr.args = ('Missing header field',) + verr.args
        raise
    
    return indexes

def extract_info(csv_string, mapping):
    """
    extract relevant information from a comma separated input string
    PARAMETERS
    csv_string: input string containing comma separated information
    mapping: python dictionary with field->index mapping
    Returns a tuple of ip address string, datetime object and document name
    """
    # get one line 
    line = csv_string.rstrip('\n').split(',')
    
    # extract ip address
    ip_address = line[mapping['ip']]
    
    # create data time object
    d = ' '.join((line[mapping['date']], line[mapping['time']]))
    datetime_obj = datetime(int(d[:4]),  int(d[5:7]),  int(d[8:10]),
                                int(d[11:13]),  int(d[14:16]),  int(d[17:]) )
#    datetime_obj = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
    
    # extract document title
    web_doc = ''.join((line[mapping['cik']], line[mapping['accession']], \
                        line[mapping['extention']]))
    
    return ip_address, datetime_obj, web_doc

def end_all_session(sessions_dict, fp):
    """
    End all currently open session and write them to file
    PARAMETERS
    sessions_dict: ordered dictionary containing session info
    fp: output file pointer
    """
    # list to capture each line
    endsession = []
    
    # here we need to order session by their start time
    # x[1] is the value of session_dict (key is ip address)
    # x[1][0] is the start time of each session
    for ip, attrib in sorted(sessions_dict.items(), key = lambda x: x[1][0]):
        start_dt, stop_dt, count = attrib
        # compose string
        session2write = compose_output_string(ip, start_dt, stop_dt, count)
        # add to list
        endsession.append(session2write)
    
    # write all sessions to file
    endsession2write = ''.join(endsession)
    fp.write(endsession2write)

def compose_output_string(ip, start_dt, stop_dt, count):
    """
    Compose output string
    ip: ip address (string)
    start_dt: session start date and time (datetime object)
    stop_dt: session stop date and time (datetime object)
    count: document count for that session (integer)
    Returns a comma separated string
    """
    compo = ','.join((
              ip,
              '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
                                           start_dt.year,
                                           start_dt.month,
                                           start_dt.day,
                                           start_dt.hour,
                                           start_dt.minute,
                                           start_dt.second),
              '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(
                                           stop_dt.year,
                                           stop_dt.month,
                                           stop_dt.day,
                                           stop_dt.hour,
                                           stop_dt.minute,
                                           stop_dt.second),
    #          start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
    #          stop_datetime.strftime('%Y-%m-%d %H:%M:%S'),
              str(int((stop_dt-start_dt).total_seconds())+1),
              str(count)
              )) + '\n'
              
    return compo

def close_sessions(sessions, timetamp, delta, fp):
    """
    Determine what session ended, close them and write them to file
    PARAMETERS
    sessions: open session dictionary
    timestamp: current datetime
    delta: inactivity period in seconds
    fp: output file pointer
    """
    # Check if we can close any open session first
    ip2close = []
    for ip, s in sessions.items():
        # is this session inactive?
        if timetamp - s[1] > delta:
            # close session, mark it for output
            ip2close.append(ip)
        else:
            # any later session will stay open
            break
    
    # remove closed session and stream it to output file
    for ipdone in ip2close:
        start_datetime, stop_datetime, count = sessions.pop(ipdone)
        session2write = compose_output_string(ipdone, start_datetime,
                                              stop_datetime, count)
        # python takes care of OS newline dependencies
        fp.write(session2write)

def update_sessions(sessions, timetamp, ip):
    """
    Update existing session or create a new session
    PARAMETERS
    sessions: open session dictionary
    timestamp: current datetime
    ip: current ip address
    """
    # update sessions dictionary
    if not sessions.get(ip, False):
        # create new session entry
        sessions[ip] = [timetamp, timetamp, 1]
    else:
        if timetamp > sessions[ip][1]:
            # Remove session
            start_datetime, stop_datetime, count = sessions.pop(ip)
            # append update to the end (dict sorted by stop datetime)
            sessions[ip] = [start_datetime, timetamp, count+1]
        else:
            # time has not moved forward, keep same session order
            # increment count only
            sessions[ip][2] += 1
    # return updated sessions
    return sessions

def is_valid_file(filepath, ext):
    """
    Check that file exists but does not open
    Check that file extension is as expected
    PARAMETERS
    filepath: complete file path
    ext: expected file extension (for instance .csv)
    """    
    
    # check for file
    if not os.path.isfile(filepath):
        # Argparse uses the ArgumentTypeError to give a rejection message
        raise argparse.ArgumentTypeError(
                '\n{0} does not exist'.format(os.path.normpath(filepath)))
    
    # check file extension
    check_extension(filepath, ext)

def check_extension(filepath, ext):
    """
    Raise argparse exception is file extension does not match expected value
    PARAMETERS
    filepath: complete file path
    ext: expected file extension (for instance .csv)
    """
    # extract file extension
    path, file_extension = os.path.splitext(filepath)
    
    # check for extension
    if not file_extension == ext:
        filename = os.path.basename(path)
        filename_wext = ''.join([filename, file_extension])
        filename_wext_exp = ''.join([filename, ext])
        raise argparse.ArgumentTypeError(
            '\n{0} file NOT accepted\n Only {1} file'.format(filename_wext,
                                                           filename_wext_exp))


#### The Main program, can be used as a script or as a module
if __name__ == "__main__":
    pass