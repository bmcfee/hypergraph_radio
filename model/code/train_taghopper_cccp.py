#!/usr/bin/env python
'''
CREATED:2011-11-08 11:21:39 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Train a taghopper model using CCCP

Usage:

./train_taghopper_cccp.py featuremap_binarytags.pickle playlists_train.pickle model_out.pickle

'''

import taghopper
import numpy
import scipy.optimize
import sys
import cPickle as pickle

TOLERANCE   = 1e-4
MAXITER     = 20

def evaluateModel(mu, Pv):

    S = len(Pv)
    f = 0

    for pv in Pv:
        fn  = numpy.log(numpy.dot(mu, pv[0][1])) - numpy.log(sum(mu))
        for (v1, v2) in pv:
            fn  += numpy.log(numpy.dot(mu, v1)) - numpy.log(numpy.dot(mu, v2))
        f   += fn 
        pass

    return f / S

def computeGradient(mu, Pv):

    S   = len(Pv)
    df  = 0

    for pv in Pv:
        
        dfn = pv[0][1] / numpy.dot(mu, pv[0][1])

        for (v1, v2) in pv:
            dfn += v1 / numpy.dot(mu, v1)
            dfn -= v2 / numpy.dot(mu, v2)

        df += dfn 

    return df / S


def f_major(mu, *args):

    Pv, eta =   list(args)
    S       =   len(Pv)

    g       =   0
    dg      =   numpy.zeros_like(mu)

    for pv in Pv:

        # compute u(mu), grad_u(mu)
        u           = numpy.log(numpy.dot(mu, pv[0][1]))
        du          = pv[0][1] / numpy.dot(mu, pv[0][1])

        # compute grad_v(mu), mu' grad_v(mu)
        dv_eta      = numpy.ones_like(eta) / numpy.sum(eta)
        
        for (v1, v2) in pv:
            u       += numpy.log(numpy.dot(mu, v1))
            du      += v1 / numpy.dot(mu, v1)

            dv_eta  += v2 / numpy.dot(eta, v2)
            pass

        g   -= (u   - numpy.dot(mu, dv_eta))
        dg  -= (du  - dv_eta)

        pass

    return g / S, dg / S


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

    M           = taghopper.Model(X)

    print '%5d playlists' % len(P)

    # pre-compute the playlist vectors
    Pv = vectorize(M, P)

    fold        = numpy.inf

    for iteration in xrange(MAXITER):

        mu_new, f_hat, d = scipy.optimize.fmin_l_bfgs_b(    func    =   f_major, 
                                                            x0      =   M.mu, 
                                                            fprime  =   None, 
                                                            args    =   (Pv, M.mu),
                                                            bounds  =   [(0, None)] * len(M.mu))

        f               = evaluateModel(M.mu, Pv)

        print (u"%5d: \u2112: %.5f, \u0394=%.5e, calls=%d" % (iteration, f, f - fold, d['funcalls'])).encode('utf-8')

        if numpy.abs(f - fold) < TOLERANCE:
            break

        fold    = f
        M.mu    = mu_new

        pass
    
    M.mu        /= numpy.sum(M.mu)

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
