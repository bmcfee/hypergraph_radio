#!/usr/bin/env python
'''
CREATED:2011-10-05 10:25:33 by Brian McFee <bmcfee@cs.ucsd.edu>

Partition an array of playlists into N pickles

Usage:
./partitionPlaylists.py playlists.pickle N output_prefix
'''

import sys
import cPickle as pickle

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]


def partitionPickle(inpickle, N, outprefix):

    with open(inpickle, 'r') as f:
        X = pickle.load(f)

    for (i,Z) in enumerate(split_list(X, N)):
        with open('%s_%d.pickle' % (outprefix, i), 'w') as f:
            pickle.dump(Z, f)
    pass
    

if __name__ == '__main__':
    partitionPickle(sys.argv[1], int(sys.argv[2]), sys.argv[3])
