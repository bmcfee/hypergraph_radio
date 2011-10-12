#!/usr/bin/env python
'''
CREATED:2011-10-11 14:34:06 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Test HMM on playlist data

Usage:

./testHMM.py model.pickle test_set.pickle

'''

import cPickle as pickle
import numpy
import sys, os
import clustering
import playlist
import itertools

def loadPlaylists(inpickle):

    P = []
    with open(inpickle,'r') as f:
        playlists = pickle.load(f)

    for q in playlists:
        P.append(playlist.Playlist(q))
    return P

def testHMM(model_pickle, test_pickle):

    playlists   = loadPlaylists(test_pickle)
    m           = len(playlists)

    step        = numpy.ceil(m / 10.0)

    with open(model_pickle, 'r') as f:
        model = pickle.load(f)
    n           = len(model['C'])


    print 'Testing %d-state chain on %d playlists: [%s]%s' % (n, m, ' ' * 10, '\b' * 11),

    e_ll = 0
    for (k, p) in enumerate(playlists):
        ll = p.likelihood(model) / len(p)
        e_ll    += ll / m
        if k % step == 0:
            print '\b.',

    print '\b]\nAverage log-likelihood: %.5e' % e_ll


if __name__ == '__main__':

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    testHMM(sys.argv[1], sys.argv[2])
    pass
