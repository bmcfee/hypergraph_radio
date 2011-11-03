#!/usr/bin/env python
'''
CREATED:2011-11-03 11:16:11 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Train a taghopper model

Usage:

./train_taghopper.py featuremap_binarytags.pickle playlists_train.pickle model_out.pickle

'''


import taghopper
import numpy
import sys
import cPickle as pickle

TOLERANCE   = 1e-3
MAXITER     = 1000


def evaluateModel(M, P):

    S = len(P)
    f = 0

    for p in P:
        f += M.playlistlikelihood(p) / S

    return f


def computeGradient(M, P):

    S   = len(P)
    df  = 0

    for p in P:
        df += M.gradient(p) / S

    return df

def reducedGradient(mu, v):

    z   = numpy.argmax(v)
    rg  = numpy.zeros_like(v)

    for i in xrange(len(mu)):
        if mu[i] > 0 and i != z:
            rg[i] = v[i] - v[z]
            rg[z] -= rg[i]

    max_step = numpy.inf
    for i in xrange(len(mu)):
        if rg[i] < 0 and max_step > -mu[i] / rg[i]:
            max_step = -mu[i] / rg[i]

    return (rg, max_step)

def lineSearch(M, P, rdf, max_step):

    tmax = 0
    vmax = -numpy.inf
    for t in numpy.linspace(0, max_step):
        M.mu += t * rdf
        v = evaluateModel(M, P)
        if v > vmax:
            tmax = t
            vmax = v
        M.mu -= t * rdf
        pass

    return tmax

def displayVector(X, v):

    for t in xrange(len(v)):
        if v[t] > 0:
            print '%30s: %.3f' % (X.tagnum(t), v[t])

    pass


def trainModel(X, P):

    M = taghopper.Model(X)

    muold       = M.mu.copy()
    fold        = numpy.inf
    converged   = False

    print '%5d playlists' % len(P)
    # TODO:   2011-11-03 11:58:33 by Brian McFee <bmcfee@cs.ucsd.edu>
    # move gradient/objective computations out of Model
    # cache the update vectors
    # double-check the reduced gradient computation

    for iteration in xrange(MAXITER):

        # Correct numerical errors
        M.mu[M.mu < 0] = 0
        M.mu    /= sum(M.mu)

        f   = evaluateModel(M, P)

        if numpy.abs(f - fold) < TOLERANCE:
            converged = True
            break

        print (u"%5d: \u2112: %.5f, \u0394=%.5e" % (iteration, f, f - fold)).encode('utf-8')
        df  = computeGradient(M, P)

        (rdf, max_step) = reducedGradient(M.mu, df)

        t       = lineSearch(M, P, rdf, max_step)
        muold   = M.mu
        fold    = f
        M.mu    = M.mu.copy() + t * rdf
        pass

    return M


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        X = pickle.load(f)['X']
    with open(sys.argv[2], 'r') as f:
        P = pickle.load(f)
    
    M = trainModel(X, P)

    with open(sys.argv[3], 'w') as f:
        pickle.dump(M, f)
    pass
