#! /usr/bin/env python
'''
train_scenario [OPTIONS] <SCENARIO_PATH>

Creates a SUNNY knowledge base corresponding to the ASlib scenario contained in 
<SCENARIO_PATH>. A knowledge base <KB> is basically a folder containing 3 files:

  <KB>.infos  contains the runtimes and the feature vectors 
  
  <KB>.lims   contains the lower/upper bounds for each feature
  
  <KB>.args   contains the arguments needed for SUNNY predictions


Options
=======
  --feat-range <LB>,<UB>
  Scales the feature in the range [LB, UB]. The default value is -1,1.
  --feat-def <VALUE>
  The default value for a missing/non-numeric feature. The default value is -1.
  --discard
  Discards the instances not solvable by any solver. Unset by default.
  --kb-path <PATH>
  Creates the SUNNY knowledge base at the specified path. By default, it is 
  created in the current working directory.
  --kb-name <NAME>
  Creates the SUNNY knowledge base with the specified name, i.e., it creates a 
  folder <PATH>/<NAME> containing the knowledge base (where <PATH> is the given 
  knowledge base path). The default name is kb_<SCENARIO>, where <SCENARIO> is 
  the name of the folder containing the given scenario.
'''

import os
import csv
import sys
import json
import getopt
from math import isnan

def parse_arguments(args):
  '''
  Parse the options specified by the user and returns the corresponding
  arguments properly set.
  '''
  try:
    options = [
      'feat-range=', 'feat-def=', 'kb-path=', 'kb-name=', 'help', 'discard'
    ]
    opts, args = getopt.getopt(args, None, options)
  except getopt.GetoptError as msg:
    print msg
    print 'For help use --help'
    sys.exit(2)
  
  if not args:
    if not opts:
      print 'Error! No arguments given.'
      print 'For help use --help'
      sys.exit(2)
    else:
      print __doc__
      sys.exit(0)

  scenario = args[0]
  if scenario[-1] != '/':
    scenario += '/'
  if not os.path.exists(scenario):
    print 'Error: Directory ' + scenario + ' does not exists.'
    print 'For help use --help'
    sys.exit(2)
    
  # Initialize variables with default values.
  lb = -1
  ub =  1
  feat_def = -1
  discard = False
  kb_path = os.getcwd()
  kb_name = 'kb_' + scenario.split('/')[-2]

  # Options parsing.
  for o, a in opts:
    if o == '--help':
      print __doc__
      sys.exit(0)
    elif o == '--feat-range':
      s = a.split(',')
      lb = float(s[0])
      ub = float(s[1])
    elif o == '--feat-def':
      feat_def = float(a)
    elif o == '--discard':
      discard = True
    elif o == '--kb-path':
      if not os.path.exists(a):
        print >> sys.stderr, 'Error! Directory ' + a + ' not exists.'
        print >> sys.stderr, 'For help use --help'
        sys.exit(2)
      if a[-1] == '/':
        kb_path = a[:-1]
      else:
        kb_path = a
    elif o == '--kb-name':
      kb_name = a

  return scenario, lb, ub, feat_def, discard, kb_path, kb_name


def parse_description(path):
  '''
  Parse the file description.txt of the scenario contained in path. It returns:
    - the list of the algorithms of the scenario;
    - the runtime limit for the scenario;
    - the number of features used in the scenario.
  '''
  reader = csv.reader(open(path + 'description.txt'), delimiter = ':')
  num_features = 0
  pfolio = []
  for row in reader:
    key = row[0]
    if key == 'algorithm_cutoff_time':
      timeout = float(row[1])
    elif key in ['algorithms_deterministic', 'algorithms_stochastic']:
      pfolio += [x.strip() for x in row[1].split(',') if x.strip()]
    elif key in ['features_deterministic', 'features_stochastic']:
      num_features += len([x for x in row[1].split(',') if x.strip()])
  return pfolio, timeout, num_features

def main(args):
  # Setting variables.
  scenario, lb, ub, feat_def, discard, kb_path, kb_name = parse_arguments(args)
  pfolio, timeout, num_features = parse_description(scenario)
  kb_dir = kb_path + '/' + kb_name + '/'
  if not os.path.exists(kb_dir):
    os.makedirs(kb_dir)
  else:
    print >> sys.stderr, 'Error! Directory ' + kb_dir + ' already exists.'
    print >> sys.stderr, 'Please choose another name.'
    sys.exit(2)

  # Creating <KB>.info
  writer = csv.writer(open(kb_dir  + kb_name + '.info', 'w'), delimiter = '|')
  # Processing runtimes.
  reader = csv.reader(open(scenario + 'algorithm_runs.arff'), delimiter = ',')
  for row in reader:
    if row and row[0].strip().upper() == '@DATA':
      # Iterates until preamble ends.
      break
  kb = {}
  for row in reader:
    inst   = row[0]
    solver = row[2]
    info   = row[4]
    if info != 'ok':
      time = timeout
    else:
      time = float(row[3])
    if inst not in kb.keys():
      kb[inst] = {}
    kb[inst][solver] = {'info': info, 'time': time}
  # Processing features.
  reader = csv.reader(open(scenario + 'feature_values.arff'), delimiter = ',')
  for row in reader:
    if row and row[0].strip().upper() == '@DATA':
      # Iterates until preamble ends.
      break
  features = {}
  lims = {}
  instances = []
  for row in reader:
    inst = row[0]
    if inst not in instances:
      instances.append(inst)
    nan = float("nan")
    feat_vector =[]
    for f in row[2:]:
      if f == '?':
        feat_vector.append(float("nan"))
      else:
        feat_vector.append(float(f))
    if not lims:
      for k in range(0, len(feat_vector)):
        lims[k] = [float('+inf'), float('-inf')]
    # Computing min/max value for each feature.
    for k in range(0, len(feat_vector)):
      if not isnan(feat_vector[k]):
        if feat_vector[k] < lims[k][0]:
          lims[k][0] = feat_vector[k]
        if feat_vector[k] > lims[k][1]:
          lims[k][1] = feat_vector[k]
    features[inst] = feat_vector
    assert len(feat_vector) == num_features
  # Scaling features.
  for (inst, feat_vector) in features.items():
    if discard and not [s for s, it in kb[inst].items() if it['info'] == 'ok']:
      # Instance not solvable by any solver.
      continue
    new_feat_vector = []
    for k in range(0, len(feat_vector)):
      if lims[k][0] == lims[k][1]:
        # Ignore constant features.
        continue
      if isnan(feat_vector[k]):
        new_val = feat_def
      else:
        min_val = lims[k][0]
        max_val = lims[k][1]
        # Scale feature value in [lb, ub].
        x = (feat_vector[k] - min_val) / (max_val - min_val)
        new_val = lb + (ub - lb) * x
      assert lb <= new_val <= ub
      new_feat_vector.append(new_val)
    assert nan not in new_feat_vector
    kb_row = [inst, new_feat_vector, kb[inst]]
    writer.writerow(kb_row)

  # Creating <KB>.lims and <KB>.args
  lim_file = kb_dir + kb_name + '.lims'
  with open(lim_file, 'w') as outfile:
    json.dump(lims, outfile)
  writer = csv.writer(open(kb_dir + kb_name + '.args', 'w'), delimiter = '|')
  writer.writerow(
    [lb, ub, feat_def, timeout, num_features, pfolio, len(instances)]
  )

if __name__ == '__main__':
  main(sys.argv[1:])
