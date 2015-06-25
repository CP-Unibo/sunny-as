#! /usr/bin/env python

'''
pre_process [OPTIONS] <SCENARIO_PATH>

Computes the SUNNY pre-solving phase and sets the corresponding arguments.

Note that feature selection is performed by using WEKA tool, and in particular 
the supervised attribute filter:

  weka.filters.supervised.attribute.AttributeSelection

which allows various search and evaluation methods to be combined.

Options
=======

--kb-path <PATH>
  PATH of the SUNNY knowledge base for the specified scenario. By default, it is 
  set to <SCENARIO_PATH>
  
--static-schedule 
  Computes a static schedule. If set, computes a static schedule (B, C) where:
    B: is the backup solver of the given scenario.
    C: is T/(M * 10), where T is the timeout and M the number of algorithms of 
       the given scenario.
  By default, this option is unset.
  TODO: Add more options for static scheduling.
  
-S <SEARCH CLASS>
  Sets the search method and its options for WEKA subset evaluators, e.g.:
    -S "weka.attributeSelection.BestFirst -S 8"
  This option is allowed only in conjunction with -E option.
  (TBD)
  
-E <ALGORITHM>
  Sets the attribute/subset evaluator and its options, e.g.:
    -E "weka.attributeSelection.CfsSubsetEval -L"
  This option is allowed only in conjunction with -S option.
  (TBD)
  
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
    opts, args = getopt.getopt(
      args, 'S:E:', ['help', 'static-schedule', 'kb-path=']
    )
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
  evaluator = ''
  search = ''
  static_schedule = False
  kb_path = scenario
  kb_name = 'kb_' + scenario.split('/')[-2]

  # Options parsing.
  for o, a in opts:
    if o == '--help':
      print __doc__
      sys.exit(0)
    elif o == '-E':
      evaluator = a
    elif o == '-S':
      search = a
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
  info_file = kb_path + '/' + kb_name + '.info'
  return args_file, info_file, scenario, evaluator, search, static_schedule

def select_features(args, info_file, evaluator, search):
  
  # ****************************************************************************
  # TODO: Tong, please implement this function.
  # args = python dict containing the arguments of SUNNY (e.g., selected_features, 
  #  feature_steps,...)
  # info_file = path of csv file containing feature vectors and runtime infos for each instance
  # evaluator = WEKA evaluator command
  # search = WEKA search command
  
  #weka_cmd = 'java -cp weka.jar weka.filters.supervised.attribute.AttributeSelection ' + evaluator + search
  #....
  
  # new_features will be the list of the selected features. This is a dummy test
  # which selects all the training features.
  selected_features = args['selected_features']
  feature_steps = args['feature_steps']
  new_features = selected_features.keys()
  #
  #*****************************************************************************
  
  selected_features = dict(
    (feature, index) 
    for (feature, index) in selected_features.items() 
    if feature in new_features
  )
  feature_steps = dict(
    (step, features) 
    for (step, features) in feature_steps.items()
    if set(features).intersection(new_features)
  )
  return selected_features, feature_steps
  

def compute_schedule(args, max_time = 10):
  # TODO: Fabio, here you can try different static schedules (maybe setting a 
  # corresponding options, e.g. --static-schedule <...>)
  solver = args['backup']
  time = args['timeout'] / (10 * len(args['portfolio']))
  return [(solver, min(time, max_time))]

def main(args):
  args_file, info_file, scenario, evaluator, search, static_schedule = \
    parse_arguments(args)
  with open(args_file) as infile:
    args = json.load(infile)
  infile.close()
  
  # Feature selection.
  if evaluator and search:
    selected_features, feature_steps = select_features(
      args, info_file, evaluator, search
    )
    args['selected_features'] = selected_features
    args['feature_steps'] = feature_steps
  
  # Static schedule.
  if static_schedule:
    static_schedule = compute_schedule(args)
    args['static_schedule'] = static_schedule
    
  with open(args_file, 'w') as outfile:
    json.dump(args, outfile)
    
if __name__ == '__main__':
  main(sys.argv[1:])