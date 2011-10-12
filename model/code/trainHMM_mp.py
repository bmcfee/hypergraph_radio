#!/usr/bin/env python
'''
CREATED:2011-10-11 21:22:35 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Train a transparent HMM for playlists with multi-threading

Usage:

./trainHMM_mp.py NUM_THREADS training_set.pickle model_output.pickle clustering_1 clustering_2 ...

'''

import cPickle as pickle
import numpy
import sys, os
import clustering
import playlist
import itertools

import multiprocessing as mp

TOLERANCE = 1e-5

def loadPlaylists(inpickle):

    P = []
    with open(inpickle,'r') as f:
        playlists = pickle.load(f)

    for q in playlists:
        P.append(playlist.Playlist(q))
    return P

def loadClusterings(cluster_pickles):

    clusterings = []

    for q in cluster_pickles:
        with open(q, 'r') as f:
            C = pickle.load(f)
            clusterings.append(C['C'])
    return clusterings

def mt_estep(num_threads, playlists, model, step, n, m):

    def consumer(Q_in, Q_out, model):
        while True:
            try:
                p = in_Q.get(True, 1)
                (g, xi, ll) = p.forwardBackward(model)
                Q_out.put( (g, xi, ll / len(p)) )
            except:
                break

        Q_out.close()
        return

    # Queue up
    in_Q = mp.Queue()
    out_Q = mp.Queue()
    print '[%s]%s' % (' ' * 10, '\b' * 11),
    for (k, p) in enumerate(playlists):
        in_Q.put(p)
        if k % step == 0:
            print '\b.',

    for i in range(num_threads):
        mp.Process(target=consumer, args=(in_Q, out_Q, model)).start()
        pass

    gamma = numpy.zeros(n)
    xi    = numpy.zeros((n,n))
    mll   = 0
    print '%s[%s]%s' % ('\b' * 13, ' ' * 10, '\b' * 11),

    for k in range(m):
        (e_g, e_xi, e_mll) = out_Q.get(True)
        gamma   += e_g / m
        xi      += e_xi / m
        mll     += e_mll / m

        if k % step == 0:
            print '\b#',
        pass

    return (gamma, xi, mll)



def trainHMM(num_threads, training_set_pickle, clustering_pickles):

    playlists   = loadPlaylists(training_set_pickle)
    m           = len(playlists)
    step        = numpy.ceil(m / 10.0)

    model       = {'C': loadClusterings(clustering_pickles)}
    n           = len(model['C'])
    model['A']  = numpy.ones((n,n)) / n
    model['pi'] = numpy.ones(n) / n

    print
    print 'Training %d-state chain with %d playlists on %d threads' % (n, m, num_threads)

    mll         = -numpy.infty
    for i in itertools.count(1):
        # E-step

        print '%04d: ' % i,
        (e_gamma, e_xi, e_mll) = mt_estep(num_threads, playlists, model, step, n, m)

        print u"\b]: LL: %.5e, Delta=%.5e" % (e_mll, e_mll - mll)
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

    model = trainHMM(int(sys.argv[1]), sys.argv[2], sys.argv[4:])
    with open(sys.argv[3], 'w') as f:
        pickle.dump(model, f)
    pass
