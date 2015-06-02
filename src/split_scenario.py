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
  --random
    Creates a random splitting of the training and test sets (by using the same 
    number of repetition and folds). This option is unset by default.
'''

import sys
import csv

def main(args):
  pass

if __name__ == '__main__':
  main(sys.argv[1:])