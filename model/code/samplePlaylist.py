#!/usr/bin/env python
'''
CREATED:2011-10-13 13:31:54 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Sample a playlist from a model file

Usage:

./samplePlaylist.py model.pickle songhash.pickle N
'''

import clustering
import sys
import cPickle as pickle
import numpy, numpy.random
import pprint


def sampleFromMultinomial(p):
    for (i,v) in enumerate(numpy.random.multinomial(1, p)):
        if v > 0:
            return i
    pass

def sampleFromModel(N, model):

    # pick the initial state
    x           = sampleFromMultinomial(model['pi'])
    playlist    = [model['C'][x].sample()]

    states      = ['---']
    for i in range(N):
        # sample a new state
        states.append(model['C'][x].getDescription())
        x   = sampleFromMultinomial(model['A'][x])
        playlist.append(model['C'][x].sample(playlist[-1]))
    return zip(playlist, states)

def samplePlaylist(N, model, songs):

    for (i,(x, s)) in enumerate(sampleFromModel(N, model)):
        print '%2d. [%16s] %s' % (i, s, songs[x])
    pass

if __name__ == '__main__':
    with open(sys.argv[2], 'r') as f:
        model = pickle.load(f)
    with open(sys.argv[3], 'r') as f:
        songs = pickle.load(f)

    samplePlaylist(int(sys.argv[1]), model, songs)
    pass
