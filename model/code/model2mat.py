#!/usr/bin/env python
'''
CREATED:2011-10-11 18:49:13 by Brian McFee <bmcfee@cs.ucsd.edu>

Convert a HMM model output to matlab file

Usage:

./model2mat.py model.pickle model.mat
'''

import sys, cPickle as pickle
import scipy.io
import numpy

with open(sys.argv[1], 'r') as f:
    model = pickle.load(f)

scipy.io.savemat(sys.argv[2], {'A': model['A'], 'p': model['pi'], 'names': [x.getDescription() for x in model['C']]}, oned_as='column')
