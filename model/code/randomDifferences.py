#!/usr/bin/env python
'''
CREATED:2011-10-18 13:57:18 by Brian McFee <bmcfee@cs.ucsd.edu>
  
Compute pairwise difference vectors of N random pairs of songs

Usage:

./randomDifferences.py featuremap.pickle N output.txt
'''

import sys
import cPickle as pickle
import clustering
import numpy
import random

def randomDifferences(feature_P, N, output_F):

    with open(feature_P, 'r') as f:
        X = pickle.load(f)['X']

    ids = X.keys()

    D = []

    for i in range(N):
        (x,y) = random.sample(ids, 2)
        D.append(X[x] - X[y])
        pass

    numpy.savetxt(output_F, D, fmt="%.4f")
    pass


if __name__ == '__main__':
    randomDifferences(sys.argv[1], int(sys.argv[2]), sys.argv[3])
