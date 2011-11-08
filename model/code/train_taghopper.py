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

TOLERANCE   = 1e-4
MAXITER     = 1000

def evaluateModel(mu, Pv):

    S = len(Pv)
    f = 0

    for pv in Pv:
#         m   = len(pv) + 1
        fn  = numpy.log(numpy.dot(mu, pv[0][1])) - numpy.log(sum(mu))
        for (v1, v2) in pv:
            fn  += numpy.log(numpy.dot(mu, v1)) - numpy.log(numpy.dot(mu, v2))
        f   += fn 
        pass

    return f / S

def computeGradient(mu, Pv):

    S   = len(P)
    df  = 0

    for pv in Pv:
#         m = len(pv) + 1
        
        dfn = pv[0][1] / numpy.dot(mu, pv[0][1])

        for (v1, v2) in pv:
            dfn += v1 / numpy.dot(mu, v1)
            dfn -= v2 / numpy.dot(mu, v2)

        df += dfn 

    return df / S

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

def lineSearch(M, Pv, rdf, max_step):

    tmax = 0
    vmax = -numpy.inf
    for t in numpy.linspace(0, max_step):
        v = evaluateModel(M.mu + t * rdf, Pv)
        if v > vmax:
            tmax = t
            vmax = v
        pass

    return tmax

def displayVector(X, v):

    for t in xrange(len(v)):
        if v[t] > 0:
            print '%30s: %.3f' % (X.tagnum(t), v[t])

    pass

def vectorize(M, P):
    Pv = []
    for p in P:
        Pvn = []
        for i in range(0, len(p)-1):
            Pvn.append(M.transitionVectors(p[i], p[i+1]))
        Pv.append(Pvn)
        pass
    return Pv

def trainModel(X, P):

    M = taghopper.Model(X)

    muold       = M.mu.copy()
    fold        = numpy.inf
    converged   = False

    print '%5d playlists' % len(P)

    # pre-compute the playlist vectors
    Pv = vectorize(M, P)

    for iteration in xrange(MAXITER):

        # Correct numerical errors
        M.mu[M.mu < 0]  = 0
        M.mu            /= sum(M.mu)

        f               = evaluateModel(M.mu, Pv)

        if numpy.abs(f - fold) < TOLERANCE:
            converged = True
            break

        print (u"%5d: \u2112: %.5f, \u0394=%.5e" % (iteration, f, f - fold)).encode('utf-8')
        df  = computeGradient(M.mu, Pv)

        (rdf, max_step) = reducedGradient(M.mu, df)

        t       = lineSearch(M, Pv, rdf, max_step)

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
