#!/usr/bin/env python
'''
CREATED:2011-10-12 11:17:03 by Brian McFee <bmcfee@cs.ucsd.edu>

Initialize a uniform clustering from a playlist set

Usage:

./initClustering playlistSet.pickle clustering_uniform.pickle

'''

import sys
import cPickle as pickle
import clustering


def initClustering(playlistSet, outpickle):

    with open(playlistSet, 'r') as f:
        songs = pickle.load(f)['songs']
        pass

    C = clustering.Clustering(songs)
    C.setDescription('Uniform')

    with open(outpickle, 'w') as f:
        pickle.dump({'C': C}, f)

    pass


if __name__ == '__main__':
    initClustering(sys.argv[1], sys.argv[2])
    pass
