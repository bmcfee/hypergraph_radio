#!/usr/bin/env python
'''
CREATED:2011-11-03 14:59:25 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Test a taghopper model

Usage:

./test_taghopper.py model.pickle playlists_test.pickle 

'''


import taghopper
import numpy
import sys
import cPickle as pickle

def evaluateModel(mu, Pv):

    S = len(Pv)
    f = 0

    for pv in Pv:
        m   = len(pv) + 1
        fn  = numpy.log(numpy.dot(mu, pv[0][1]))
        for (v1, v2) in pv:
            fn  += numpy.log(numpy.dot(mu, v1)) - numpy.log(numpy.dot(mu, v2))
        f   += fn / m
        pass

    return f / S

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

def testModel(M, P):

    print '%5d playlists' % len(P)

    # pre-compute the playlist vectors
    Pv = vectorize(M, P)
    f  = evaluateModel(M.mu, Pv)

    print (u"\u2112: %.5f" % f).encode('utf-8')
    pass

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        M = pickle.load(f)
    with open(sys.argv[2], 'r') as f:
        P = pickle.load(f)

    testModel(M, P)
    
    pass
