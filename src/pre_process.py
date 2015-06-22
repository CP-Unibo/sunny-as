#! /usr/bin/env python

'''
pre_process [OPTIONS] <SCENARIO_PATH>

TBD
Computes the SUNNY pre-processing phase and sets the corresponding arguments.

Options
=======

--kb-path <PATH>
  PATH of the SUNNY knowledge base for the specified scenario. By default, it is 
  set to <SCENARIO_PATH>.
--feat-algorithm <ALGORITHM>
  Sets the WEKA algorithm for feature selection. Possible choices are: 
    symmetric:  cfr... TBD 
    gain_ratio: cfr... TBD
    info_gain:  cfr... TBD
  The installation of WEKA is required for this option (unset by default).
--num-features <NUM>
  The number of selected features. To be used together with --feat-algorithm 
  option. By default, <NUM> is set to 5.
--static-schedule 
  Computes a static schedule. Unset by default. (TBD)
--help
  Prints this message.
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
  try:
    options = [
      'help', 'static-schedule', 'feat-algorithm=', 'num-features=', 
      'kb-path=',
    ]
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

  scenario = args[0]
  if scenario[-1] != '/':
    scenario += '/'
  if not os.path.exists(scenario):
    print >> sys.stderr, 'Error: Directory ' + scenario + ' does not exists.'
    print >> sys.stderr, 'For help use --help'
    sys.exit(2)
    
  # Initialize variables with default values.
  feat_algorithm = None
  feat_timeout = -1
  num_features = 5
  static_schedule = False
  kb_path = scenario
  kb_name = 'kb_' + scenario.split('/')[-2]

  # Options parsing.
  for o, a in opts:
    if o == '--help':
      print __doc__
      sys.exit(0)
    elif o == '--feat-algorithm':
      if a not in ['symmetric', 'gain_ratio', 'info_gain']:
        print >> sys.stderr, 'Error! Unknown algorithm ' + a
        print >> sys.stderr, 'For help use --help'
        sys.exit(2)
      feat_algorithm = a
    elif o == '--num-features':
      num_features = int(a)
    elif o == '--static-schedule':
      static_schedule = True
    elif o == '--kb-path':
      if not os.path.exists(a):
        print >> sys.stderr, 'Error! Directory ' + a + ' not exists.'
        print >> sys.stderr, 'For help use --help'
        sys.exit(2)
      if a[-1] == '/':
        kb_path = a[:-1]
      else:
        kb_path = a
  
  kb_name = kb_path.split('/')[-2]
  args_file = kb_path + '/' + kb_name + '.args' 
  return args_file, scenario, kb_path, feat_timeout, feat_algorithm, \
    num_features, static_schedule

# PRE-MARSHALLING: selected_features[0:1]
def select_features(feat_algorithm, num_features, selected_features, args):
  # TBD
  return selected_features #[0:1]
  # Modify also feature_steps

#[(backup, T/(10*m))]
# ASP-POTASSCO: 577.5 (-)
# CSP-2010: 6617.3 (-)
# MAXSAT12-PMS: 3789.5 (-)
# PREMARSHALLING-ASTAR-2013: 2221.6 (=)
# PROTEUS-2014: 
# QBF-2011: 8981.3 (+)
# SAT11-HAND: 19070.8 (+)
# SAT11-INDU: 13111.6 (+) (backup, 1)
# SAT11-RAND: 10183.7 (-)
# SAT12-ALL: 
# SAT12-HAND: 
# SAT12-INDU: 
# SAT12-RAND: 
def compute_schedule(args):
  # TBD
  solver = args['backup']
  time = args['timeout'] / (10 * len(args['portfolio']))
  return [(solver, time)] 

  



def main(args):
  args_file, scenario, kb_path, feat_timeout, feat_algorithm, num_features, \
    static_schedule = parse_arguments(args)
  with open(args_file) as infile:
    args = json.load(infile)
  infile.close()
  
  # Feature selection.
  if feat_algorithm:
    selected_features = select_features(
      feat_algorithm, num_features, args['selected_features'], args
    )
    args['selected_features'] = selected_features
    
  # Static schedule.
  if static_schedule:
    static_schedule = compute_schedule(args)
    args['static_schedule'] = static_schedule
    
  with open(args_file, 'w') as outfile:
    json.dump(args, outfile)
    
if __name__ == '__main__':
  main(sys.argv[1:])