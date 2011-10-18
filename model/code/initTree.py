#!/usr/bin/env python
'''
CREATED:2011-10-12 11:17:03 by Brian McFee <bmcfee@cs.ucsd.edu>

Initialize the root of a spill tree from a playlist set

Usage:

./initTree.py tree_uniform.pickle playlist_set1.pickle playlist_set2.pickle ...

'''

import sys
import cPickle as pickle
import clustering


def initTree(outpickle, playlistSet):

    songs = set()
    for p in playlistSet:
        with open(p, 'r') as f:
            songs.update(pickle.load(f)['songs'])
        pass

    C = clustering.SpillTree(points=songs, description='Uniform-0')

    with open(outpickle, 'w') as f:
        pickle.dump({'C': C}, f)

    pass


if __name__ == '__main__':
    initTree(sys.argv[1], sys.argv[2:])
    pass
