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

--feat-timeout <TIME>
  Sets the maximum time allowed for a feature step: if <TIME> is exceeded, all 
  the features of the corresponding step are removed. By default is set to T/2, 
  where T is the solving timeout for the scenario.

--feat-algorithm <ALGORITHM>
  Sets the WEKA algorithm for feature selection. Possible choices are: 
    symmetric: TBD 
    gain_ratio: TBD
    info_gain: TBD
  The installation of WEKA is required for this option (unset by default).

--num-features <NUM>
  The number of selected features. To be used together with --feat-algorithm 
  option. By default, <NUM> is set to 5.

--static-schedule 
  Computes a static schedule. Unset by default. (TBD)

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
    options = [
      'help', '--static-schedule', 'max-feat-time=', 'feat-algorithm=', 
      'num-features=', 'kb-path=', 'help', 'discard'
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
    elif o == '--max-feat-time':
      feat_timeout = float(a)
    elif o == '--feat-algorithm':
      feat_algorithm = a
    elif o == '--num-features':
      num_features = int(a)
    elif o == '--static-schedule':
      # TBD
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
  args_file = kb_path + kb_name + '.args'
  with open(args_file) as infile:
    args = json.load(infile)
  infile.close()
  if not feat_timeout < 0:
    feat_timeout = args['timeout'] / 2
  
  return args, scenario, kb_path, feat_timeout, feat_algorithm, num_features, \
    static_schedule

def set_features(args):
  args['selected_features'] # = args['selected_features'][0:1]

def set_schedule(args):
  args['static_schedule'] # = [("idastar-symmulgt-transmul", 90)]
    
def main(args):
  args, scenario, kb_path, feat_timeout, feat_algorithm, num_features, \
    static_schedule = parse_arguments(args)
  
  # Too costly features.
  selected_features = args['selected_features']
  selected_features = remove_features(
    selected_features, select_features, scenario, feat_steps, feat_timeout
  )
  
  # Feature selection.
  if feat_algorithm:
    selected_features = select_features(
      feat_algorithm, num_features, selected_features
    )
    args['selected_features'] = selected_features
    
  # Static schedule.
  if static_schedule:
    static_schedule = compute_schedule(...)
    args['static_schedule'] = static_schedule
    
  with open(args_file, 'w') as outfile:
    json.dump(args, outfile)
    
if __name__ == '__main__':
  main(sys.argv[1:])