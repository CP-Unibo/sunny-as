#! /usr/bin/env python

'''
TBD
'''

import os
import csv
import sys
import json
import getopt
import shutil

def parse_arguments(args):
  '''
  Parse the options specified by the user and returns the corresponding
  arguments properly set.
  '''
  #TBD
  try:
    options = ['help'] #TBD
    opts, args = getopt.getopt(args, None, options)
  except getopt.GetoptError as msg:
    print >> sys.stderr, msg
    print >> sys.stderr, 'For help use --help'
    sys.exit(2)
  
  if not args:
    if not opts:
      print >> sys.stderr, 'Error! No arguments given.'
      print >> sys.stderr, 'For help use --help'
      sys.exit(2)
    else:
      print __doc__
      sys.exit(0)

  kb_path = args[0]
  if kb_path[-1] != '/':
    kb_path += '/'
  if not os.path.exists(kb_path):
    print >> sys.stderr, 'Error: Directory ' + kb_path + ' does not exists.'
    print >> sys.stderr, 'For help use --help'
    sys.exit(2)
    
  # Initialize variables with default values.
  #TBD

  # Options parsing.
  for o, a in opts:
    if o == '--help':
      print __doc__
      sys.exit(0)
    #TBD elif o == '...':
  
  kb_name = kb_path.split('/')[-2]
  args_file = kb_path + kb_name + '.args'
  return args_file 

def set_features(args):
  args['selected_features'] = args['selected_features'][0:1]

def set_schedule(args):
  args['static_schedule']# = [("idastar-symmulgt-transmul", 90)]
    
def main(args):
  args_file = parse_arguments(args)
  with open(args_file) as infile:
    args = json.load(infile)
  infile.close()
  set_schedule(args)
  set_features(args)
  with open(args_file, 'w') as outfile:
    json.dump(args, outfile)
    
if __name__ == '__main__':
  main(sys.argv[1:])