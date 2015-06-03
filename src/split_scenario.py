#! /usr/bin/env python

'''
split_scenario [OPTIONS] <SCENARIO_PATH>

Given the scenario path, creates 2 * N * M folders where N is the number of the 
repetition and M the number of folds of the scenario. For i = 1, ..., N and 
j = 1, ..., M each folder is called train_i_j (resp. test_i_j) and consists in a 
clone of the original scenario which only contains the training (resp. test)
instances of the scenario.

Options
=======
  --name <NAME>
    Name of the folder containing the train/test sub-folders. The default name 
    is cv_<SCENARIO>, where <SCENARIO> is the name of the folder containing the 
    given scenario.
  --path <PATH>
    Creates the cv folders at the specified path. By default, <PATH> is set to 
    the current working directory.
  --random-split
    Creates a random splitting of the training and test sets (by using the same 
    number of repetition and folds). This option is unset by default.
'''

import os
import sys
import csv
import getopt

def parse_arguments(args):
  '''
  Parse the options specified by the user and returns the corresponding
  arguments properly set.
  '''
  try:
    options = ['name=', 'path=', 'random-split=']
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
  random = False
  cv_path = os.getcwd()
  cv_name = 'cv_' + scenario.split('/')[-2]

  # Options parsing.
  for o, a in opts:
    if o == '--help':
      print __doc__
      sys.exit(0)
    elif o == '--random-split':
      discard = True
    elif o == '--path':
      if not os.path.exists(a):
        print >> sys.stderr, 'Error! Directory ' + a + ' not exists.'
        print >> sys.stderr, 'For help use --help'
        sys.exit(2)
      if a[-1] == '/':
        cv_path = a[:-1]
      else:
        cv_path = a
    elif o == '--name':
      cv_name = a

  cv_dir = cv_path + '/' + cv_name + '/'
  if not os.path.exists(cv_dir):
    os.makedirs(cv_dir)
  else:
    print >> sys.stderr, 'Warning! Directory ' + cv_dir + ' already exists.'

  return scenario, cv_dir, random

def main(args):
  scenario, cv_dir, random = parse_arguments(args)
  reader = csv.reader(open(scenario + 'cv.arff'), delimiter = ',')
  for row in reader:
    if row and row[0].strip().upper() == '@DATA':
      # Iterates until preamble ends.
      break
  cv = {}
  for row in reader:
    rep = row[1]
    fold = row[2]
    if rep not in cv.keys():
      cv[rep] = {}
    if fold not in cv[rep].keys():
      cv[rep][fold] = set([])
    cv[rep][fold].add(row[0])

if __name__ == '__main__':
  main(sys.argv[1:])