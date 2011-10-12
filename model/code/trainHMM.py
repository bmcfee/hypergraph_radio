#!/usr/bin/env python
'''
CREATED:2011-10-11 14:34:06 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Train a transparent HMM for playlists

Usage:

./trainHMM.py training_set.pickle model_output.pickle clustering_1 clustering_2 ...

'''

import cPickle as pickle
import numpy
import sys, os
import clustering
import playlist
import itertools

TOLERANCE = 1e-5

def loadPlaylists(inpickle):

    P = []
    with open(inpickle,'r') as f:
        playlists = pickle.load(f)

    for q in playlists:
        P.append(playlist.Playlist(q))
    return P[:500]

def loadClusterings(cluster_pickles):

    clusterings = []

    for q in cluster_pickles:
        with open(q, 'r') as f:
            C = pickle.load(f)
            clusterings.append(C['C'])
    return clusterings

def trainHMM(training_set_pickle, clustering_pickles):

    playlists   = loadPlaylists(training_set_pickle)
    m           = len(playlists)
    step        = numpy.ceil(m / 10.0)

    model       = {'C': loadClusterings(clustering_pickles)}
    n           = len(model['C'])
    model['A']  = numpy.ones((n,n)) / n
    model['pi'] = numpy.ones(n) / n


    print 'Training %d-state chain with %d playlists' % (n, m)

    mll         = -numpy.infty
    for i in itertools.count(1):
        # E-step
        e_gamma = numpy.zeros(n)
        e_xi    = numpy.zeros((n,n))
        e_mll   = 0
        
        print 'R%03d: [%s]%s' % (i, ' ' * 10, '\b' * 11),
        for (k, p) in enumerate(playlists):
            (g,xi,ll) = p.forwardBackward(model)
            e_gamma += g  / m
            e_xi    += xi / m
            e_mll   += (ll / len(p)) / m

            if k % step == 0:
                print '\b.',

        print '\b]: LL: %.5e, Delta=%.5e' % (e_mll, e_mll - mll)
        if abs(e_mll - mll) < TOLERANCE:
            break

        # M-step
        for j in range(n):
            model['A'][j,:] = e_xi[j,:] / numpy.sum(e_xi[j,:])  # normalize rows
            pass

        model['pi'] = e_gamma / numpy.sum(e_gamma)
        mll = e_mll
        pass
    return model

if __name__ == '__main__':

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    model = trainHMM(sys.argv[1], sys.argv[3:])
    with open(sys.argv[2], 'w') as f:
        pickle.dump(model, f)
    pass
