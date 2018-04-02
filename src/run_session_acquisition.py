# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 21:04:25 2018

@author: herma
"""

# necessary imports (part of python 2.7 and greater)
import os
import argparse
import utils
from collections import OrderedDict


# get this script path as a reference to find input/output folders
thispath = os.path.dirname(os.path.realpath(__file__))
#  list of relevant fields to extract
header_list = ['ip', 'date', 'time', 'cik', 'accession', 'extention' ]


"""
 Set up argument parser. Usage is available using -h option.
 There are two required input file arguments. Each input file must be
 located in the root->input directory
 The third argument is the name of the output file. It will be created
 in the root-> output directory (Default is sessionization.txt)
"""
parser = argparse.ArgumentParser(description='Streaming Data from EDGAR')
parser.add_argument('Input_log', metavar = 'LOG_FILE', 
                    help='csv log file in root->input folder')
parser.add_argument('Input_inactivity', metavar = 'INACTIVITY_FILE',
                    help='Text file containing the period of inactivity'
                    ' in seconds, located in root-> input folder')
parser.add_argument('Output_file', nargs='?', metavar = 'OUTPUT_FILE',
                    default = 'sessionization.txt',
                   help='(Optional) Ouput file name created in root->output folder.'
                   ' Default name is sessionization.txt')
args = parser.parse_args()


"""
 Check validity of input and output files
"""
# Input log file path
logfile_path = os.path.join(thispath, os.pardir, 'input', args.Input_log)    
# sanity check on input log file (existence and extension)
utils.is_valid_file(logfile_path, '.csv')

# Output file path
sessionfile_path = os.path.join(thispath, os.pardir, 'output', args.Output_file)
# sanity check on output file (extension only)
utils.check_extension(sessionfile_path, '.txt')

# get inactivity period
timeout_delta = utils.get_timeout(thispath, args.Input_inactivity)


"""
 Each session has a start datetime and stop datetime and document count
 We will have a dictionary of ip address contaning these information
 ordered by stop datetime
"""
open_sessions = OrderedDict()

"""
 Loop through file line by line
 Note: it would be more efficent to read by chunk of lines
 but it falls outside the scope of this project
"""
with open(logfile_path, 'r') as f, open(sessionfile_path, 'w') as fout:
    
    # figure out header-index mapping        
    indexes = utils.extract_header(f, header_list)
    
    # loop through each line
    for line_str in f:
        
        # extract relevant information
        ip_address, current_datetime, _ = utils.extract_info(line_str, indexes)
        
        # detect closed sessions and write them to output file
        ip2close = utils.close_sessions(open_sessions, current_datetime, timeout_delta, fout)
        
        # extend current session or create new one
        open_sessions = utils.update_sessions(open_sessions, current_datetime, ip_address)
        
    # no more line to read, end all session
    utils.end_all_session(open_sessions, fout)


