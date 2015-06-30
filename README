SUNNY-AS
========

SUNNY for Algorithm Selection

sunny-as tool implements the SUNNY algorithm [1] for a given ASlib [2] scenario.

*** Beta version ***


REQUIREMENTS
============

+ Python v2.x
  https://www.python.org/

+ Java (for feature selection)
  https://www.java.com

Note that currently this tool is tested only on Ubuntu 64-bit machines.


INSTRUCTIONS
============

The sources of sunny-as are all contained in the "src" folder.

For training a given scenario, use:

  train_scenario [OPTIONS] <SCENARIO_PATH>

while for testing the SUNNY performance use:

  test_scenario [OPTIONS] <SCENARIO_PATH>

If you want to first split the training/test sets according to the cross-fold 
validation indicated in the scenario (see file cv.arff) use instead:

  split_scenario [OPTIONS] <SCENARIO_PATH>

After the training, it is also possible to define a pre-solving phase with:

  pre_process [OPTIONS] <SCENARIO_PATH>

Note that for performing feature selection the file weka.jar is used.

The file evaluate_scenarios.py can be used for testing the different scenarios 
of ASlib version 1.0.1 (contained in the "data" folder).


AUTHOR
======

Roberto Amadini (amadini at cs.unibo.it)


CONTRIBUTORS
============

Fabio Biselli

Tong Liu

Jacopo Mauro


REFERENCES
==========

[1] R. Amadini, M. Gabbrielli, and J. Mauro. SUNNY: a Lazy Portfolio Approach
    for Constraint Solving 2013. In ICLP, 2014.
    
[2] Algorithm Selection Library (ASlib)
    http://www.coseal.net/aslib/