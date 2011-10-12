#!/usr/bin/env python
'''
CREATED:2011-10-11 14:34:06 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Test HMM on playlist data

Usage:

./testHMM.py NUM_THREADS model.pickle test_set.pickle

'''

import cPickle as pickle
import numpy
import sys, os
import clustering
import playlist
import itertools

import multiprocessing as mp


def loadPlaylists(inpickle):

    P = []
    with open(inpickle,'r') as f:
        playlists = pickle.load(f)

    for q in playlists:
        P.append(playlist.Playlist(q))
    return P

def testHMM(num_threads, model_pickle, test_pickle):

    playlists   = loadPlaylists(test_pickle)
    m           = len(playlists)

    step        = numpy.ceil(m / 10.0)

    with open(model_pickle, 'r') as f:
        model = pickle.load(f)
    n           = len(model['C'])

    def e_step(Q_in, Q_out, model):
        
        while True:
            try:
                p = Q_in.get(True, 1)
                Q_out.put(p.likelihood(model) / len(p))
            except:
                break

        Q_out.close()

        pass


    in_Q    = mp.Queue()
    out_Q   = mp.Queue()

    print 'Testing %d-state chain on %d playlists with %d threads' % (n, m, num_threads)
    print 'Queuing: [%s]%s' % (' ' * 10, '\b' * 11),

    for (k, p) in enumerate(playlists):
        in_Q.put(p)
        if k % step == 0:
            print '\b.',


    processes = []
    for i in range(num_threads):
        processes.append(mp.Process(target=e_step, args=(in_Q, out_Q, model)))
        processes[i].start()
        pass

    e_ll = 0
    k = 0
    print '%sReading: [%s]%s' % ('\b' * 21, ' ' * 10, '\b' * 11),
    while k < m:
        ll = out_Q.get(True)
        e_ll += ll / m
        if k % step == 0:
            print '\b.',
        k += 1
        pass

    print ']: Average log-likelihood: %.5e' % e_ll


if __name__ == '__main__':

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    testHMM(int(sys.argv[1]), sys.argv[2], sys.argv[3])
    pass
