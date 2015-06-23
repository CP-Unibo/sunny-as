import os
import csv
import json
from subprocess import Popen

in_path = os.path.realpath(__file__).split('/')[:-2]
scenarios = [
  #'ASP-POTASSCO',
  #'CSP-2010',
  #'MAXSAT12-PMS',
  #'PREMARSHALLING-ASTAR-2013',
  #'PROTEUS-2014',
  #'QBF-2011',
  #'SAT11-HAND',
  #'SAT11-INDU',
  #'SAT11-RAND',
  #'SAT12-ALL',
  #'SAT12-HAND',
  #'SAT12-INDU',
  'SAT12-RAND',
]  

for scenario in scenarios:
  print 'Evaluating scenario',scenario
  path = '/'.join(in_path) + '/data/aslib_1.0.1/' + scenario
  
  print 'Extracting runtimes'
  reader = csv.reader(open(path + '/algorithm_runs.arff'), delimiter = ',')
  runtimes = {}
  for row in reader:
    if row and row[0].strip().upper() == '@DATA':
      # Iterates until preamble ends.
      break
  for row in reader:
    inst = row[0]
    solv = row[2]
    time = float(row[3])
    info = row[4]
    if inst not in runtimes.keys():
      runtimes[inst] = {}
    runtimes[inst][solv] = [info, time]
  
  print 'Splitting scenario',scenario
  cmd = 'python split_scenario.py ' + path
  proc = Popen(cmd.split())
  proc.communicate()
  fsi = 0.0
  fsi_vbs = 0.0
  par10 = 0.0
  par10_vbs = 0.0
  n = 0
  m = 0
  p = 0
  for subdir, dirs, files in os.walk(path + '/cv_' + scenario):
    if 'train_' in subdir:
      
      print 'Training',subdir
      cmd = 'python train_scenario.py --discard ' + subdir
      proc = Popen(cmd.split())
      proc.communicate()
      test_dir = subdir.replace('train_', 'test_')
      kb_name = subdir.split('/')[-1]
      pred_file = test_dir + '/predictions.csv'
      
      print 'Pre-processing',test_dir
      cmd = 'python pre_process.py --feat-algorithm symmetric --static-schedule ' + subdir + '/kb_' + kb_name
      proc = Popen(cmd.split())
      proc.communicate()
      
      print 'Testing',test_dir
      cmd = 'python test_scenario.py -o ' + pred_file + ' --print-static -K ' \
	  + subdir + '/kb_' + kb_name + ' ' + test_dir
      proc = Popen(cmd.split())
      proc.communicate()
      
      if os.path.exists(path + '/feature_costs.arff'):
	print 'Extracting feature costs'
	args_file = subdir + '/kb_' + kb_name + '/kb_' + kb_name + '.args'
	with open(args_file) as infile:
	  args = json.load(infile)
	feature_steps = args['feature_steps']
	feature_cost = {}
	reader = csv.reader(open(path + '/feature_costs.arff'), delimiter = ',')
	for row in reader:
	  steps = set([])
	  i = 2
	  if row and '@ATTRIBUTE' in row[0] \
	  and 'instance_id' not in row[0] and 'repetition' not in row[0]:
	    if row[0].strip().split(' ')[1] in feature_steps:
	      steps.add(i)
	    i += 1
	  elif row and row[0].strip().upper() == '@DATA':
	    # Iterates until preamble ends.
	    break
	for row in reader:
	  feature_cost[row[0]] = 0
	  for i in steps:
	    if row[i] != '?':
	      feature_cost[row[0]] += float(row[i])
      
      print 'Computing fold statistics'
      reader = csv.reader(open(pred_file), delimiter = ',')
      old_inst = ''
      par = True
      args_file = subdir + '/kb_' + kb_name + '/kb_' + kb_name + '.args'
      with open(args_file) as infile:
        timeout = json.load(infile)['timeout']
      for row in reader:
        inst = row[0]
        if inst == old_inst:
          if par:
            continue
        else:
	  if not par:
	    par10 += timeout * 10
	    par = True
	    p += 1
	  n += 1
	  if os.path.exists(path + '/feature_costs.arff'):
            time = feature_cost[inst]
          else:
            time = 0.0
          times = [x[1] for x in runtimes[inst].values() if x[0] == 'ok']
	  if times:
	    m += 1
	    fsi_vbs += 1
	    par10_vbs += min(times)
	  else:
	    par10_vbs += 10 * timeout
        old_inst = inst
        solver = row[2]
        solver_time = float(row[3])
        if  runtimes[inst][solver][0] == 'ok' \
	and runtimes[inst][solver][1] <= solver_time:
	  par = True
	  if time + runtimes[inst][solver][1] >= timeout:
	    par10 += 10 * timeout
	    p += 1
	  else:
	    fsi += 1
	    par10 += time + runtimes[inst][solver][1]
        elif time + min([solver_time, runtimes[inst][solver][1]]) < timeout:
	  time += min([solver_time, runtimes[inst][solver][1]])
          par = False
        else:
	  par10 += 10 * timeout
	  par = True
	  p += 1
	  
      if not par:
        par10 += timeout * 10
        par = True
        p += 1
        
  assert p + fsi == n
  print '\n==========================================='
  print 'Scenario:',scenario
  print 'No. of instances:',n,'(',m,'solvable )'
  print 'FSI SUNNY:', fsi / n
  print 'FSI VBS:', fsi_vbs / n
  print 'PAR 10 SUNNY:', par10 / n
  print 'PAR 10 VBS:', par10_vbs / n
  print '===========================================\n'
