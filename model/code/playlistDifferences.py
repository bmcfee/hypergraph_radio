#!/usr/bin/env python
'''
CREATED:2011-10-18 13:44:34 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Compute pairwise difference vectors of adjacent songs in a playlist collection

Usage:

./playlistDifferences.py featuremap.pickle playlist.pickle output.txt
'''

import sys
import cPickle as pickle
import clustering
import numpy


def playlistDifferences(feature_P, playlist_P, output_F):

    with open(feature_P, 'r') as f:
        X = pickle.load(f)['X']

    with open(playlist_P, 'r') as f:
        P = pickle.load(f)

    D = []
    for playlist in P:
        for i in range(1, len(playlist)):
            if playlist[i-1] not in X or playlist[i] not in X:
                continue
            D.append(X[playlist[i]] - X[playlist[i-1]])

    numpy.savetxt(output_F, D, fmt="%.4f")
    pass


if __name__ == '__main__':
    playlistDifferences(sys.argv[1], sys.argv[2], sys.argv[3])
