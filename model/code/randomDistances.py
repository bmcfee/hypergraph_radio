#!/usr/bin/env python
'''
CREATED:2011-10-18 13:57:18 by Brian McFee <bmcfee@cs.ucsd.edu>
  
Compute pairwise distances of N random pairs of songs

Usage:

./playlistDistances.py featuremap.pickle N output.txt
'''

import sys
import cPickle as pickle
import clustering
import numpy
import random

def dist(x,y):
    return numpy.sqrt(numpy.sum((x -y)**2))

def randomDistances(feature_P, N, output_F):

    with open(feature_P, 'r') as f:
        X = pickle.load(f)['X']

    ids = X.keys()

    D = []

    for i in range(N):
        (x,y) = random.sample(ids, 2)
        D.append(dist(X[x], X[y]))
        pass

    numpy.savetxt(output_F, D, fmt="%.4f")
    pass


if __name__ == '__main__':
    randomDistances(sys.argv[1], int(sys.argv[2]), sys.argv[3])
