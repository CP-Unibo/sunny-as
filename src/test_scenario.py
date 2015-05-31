'''
test_scenario [OPTIONS] <INSTANCE_ID> <FEAT_VECTOR>

Options
=======
  -K <KB_DIR>
    Knowledge base path (default: $PWD).
  -s <STATIC_SCHEDULE>
    Static schedule to be run in the presolving phase. By default is empty.
  -c <COST>
    Set the feature cost. By default is 0.
  -k <NEIGH.SIZE>
    The default value is sqrt(train set size).
  -P <S1,...,Sk>
    The default values are all the solvers.
  -b <BACKUP>
    Set the Backup Solver (default: Single Best Solver).
  -T <TIMEOUT>
    Set the timeout of SUNNY algorithm (default: the time limit of the
    scenario).
  -o <FILE>
    Prints the predictions in <FILE> instead of std output
    
Output
======
  The prediction on std output as specified in the competition rules.
'''

import sys
import os
import getopt
import csv
import json
import ast
from math import sqrt
from combinations import binom, get_subset

def parse_arguments(args):
  '''
  Parse the options specified by the user and returns the corresponding
  arguments properly set.
  '''
  try:
    long_options = ['help']
    opts, args = getopt.getopt(args, 'K:s:c:k:P:b:T:o:h:', long_options)
  except getopt.GetoptError as msg:
    print msg
    print 'For help use --help'
    sys.exit(2)

  if len(args) == 0:
    print(opts, args)
    for o in opts:
      if o in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    print 'Error! No arguments given.'
    print 'For help use --help'
    sys.exit(2)
  if len(args) == 1:
    print(opts, args)
    for o in opts:
      if o in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    print 'Error! An argument missing.'
    print 'For help use --help'
  instance = args[0]
  feature_values = args[1].split(',')
    
  # Initialize variables with default values.
  kb_path = os.getcwd()
  if kb_path[-1] != '/':
    kb_path += '/'
  kb_name = kb_path.split('/')[-2]
  # KB option parsing.
  for o, a in opts:
    if o == '-K':
      if os.path.exists(a):
        kb_path = a
        if kb_path[-1] != '/':
          kb_path += '/'
        kb_name = kb_path.split('/')[-2]
      else:
        print 'Error: ' +a+ ' does not exists.'
        print 'Using default folder (cwd).'
  # Read arguments.
  if not os.path.exists(kb_path + kb_name + '.args'):
    print 'Error: ' + kb_path + kb_name + '.args does not exists.'
    sys.exit(2)    
  reader = csv.reader(open(kb_path + kb_name + '.args'), delimiter = '|')
  for row in reader:
    lb = int(row[0])
    ub = int(row[1])
    def_feat_value = float(row[2])
    timeout = float(row[3])
    portfolio = ast.literal_eval(row[5])
    instances = float(row[6])
    
  feature_cost = 0
  static_schedule = [] # TODO: not defined.
  k = int(round(sqrt(instances)))
  backup = None
  out_file = None

  # Options parsing.
  for o, a in opts:
    if o in ('-h', '--help'):
      print(__doc__)
      sys.exit(0)
    elif o == '-s':
      static_schedule = a
    elif o == '-k':
      k = int(a)
    elif o == '-c':
      feature_cost = float(a)
    elif o == '-P':
      s = a.split(',')
      for sol in s:
        portfolio.append(sol)
    elif o == '-b':
      backup = a
    elif o == '-T':
      timeout = float(a)
    elif o == '-o':
      out_file = a

  return lb, ub, def_feat_value, kb_path, kb_name, static_schedule, timeout, \
    k, portfolio, backup, out_file, feature_values, feature_cost, instance, instances
  
def main(args):
  lb, ub, def_feat_value, kb_path, kb_name, static_schedule, timeout, k, \
    portfolio, backup, out_file, feature_values, feature_cost, \
    instance, instances = parse_arguments(args)    
    
  with open(kb_path + kb_name + '.lims') as infile:
    lims = json.load(infile)
  
  feats = normalize(feature_values, lims, lb, ub, def_feat_value)
  kb = kb_path + kb_name + '.info'
  neighbours, new_backup = get_neighbours(feats, kb, portfolio, k, timeout,
                                          instances)
  if not backup:
    backup = new_backup
  if timeout > feature_cost: 
    schedule = get_schedule(neighbours, timeout - feature_cost,
                              portfolio, k, backup)
  else:
    schedule = []
  runID = 1
  if out_file:
    writer = csv.writer(open(out_file, 'w'), delimiter = ',')
    for sch in schedule:
      writer.writerow(str(instance) + ',' + str(runID) + ',' + str(sch[0]) + ',' +
                      str(sch[1]))
      runID += 1
  else:
    for sch in schedule:
      print(str(instance) + ',' + str(runID) + ',' + str(sch[0]) + ',' +
            str(sch[1]))
      runID += 1  
  
if __name__ == '__main__':
  main(sys.argv[1:])