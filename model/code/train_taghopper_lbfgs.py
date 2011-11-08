#!/usr/bin/env python
'''
CREATED:2011-11-08 14:23:04 by Brian McFee <bmcfee@cs.ucsd.edu>
  
Train a taghopper model using lbfgs on full (non-convex) objective

Usage:

./train_taghopper_lbfgs.py featuremap_binarytags.pickle playlists_train.pickle model_out.pickle

'''

import taghopper
import numpy
import scipy.optimize
import sys
import cPickle as pickle


def f_obj(mu, Pv):

    S = len(Pv)
    f = 0
    g = numpy.zeros_like(mu)

    summu       = numpy.sum(mu)
    logsummu    = numpy.log(summu)

    for pv in Pv:
        muv2    = numpy.dot(mu, pv[0][1])
        f      += numpy.log(muv2) 
        g      += pv[0][1] / muv2

        for (v1, v2) in pv:
            muv1 = numpy.dot(mu, v1)
            muv2 = numpy.dot(mu, v2)
            f   += numpy.log(muv1) - numpy.log(muv2)
            g   += v1 / muv1 - v2 / muv2
            pass
        pass

    return -f / S + logsummu, -g / S + numpy.ones_like(mu)/summu

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

    mu_new, f, d = scipy.optimize.fmin_l_bfgs_b(    func    =   f_obj, 
                                                    x0      =   M.mu, 
                                                    fprime  =   None, 
                                                    args    =   (Pv,),
                                                    bounds  =   [(0, None)] * len(M.mu),
                                                    iprint  =   1)

    print (u"\u2112: %.5f, calls=%d" % (f, d['funcalls'])).encode('utf-8')

    M.mu    = mu_new / numpy.sum(mu_new)

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
