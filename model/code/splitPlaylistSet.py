#!/usr/bin/env python
'''
CREATED:2011-10-11 11:19:58 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Partition a playlist set into training and test

Usage:

./splitPlaylistSet.py playlistset.pickle %TRAIN[eg, 0.75] train_out.pickle test_out.pickle
'''

import sys
import cPickle as pickle
import random


def getLists(P, ids):

    lists = []

    for x in ids:
        for y in P[x]:
            lists.append(y)
    return lists

def splitPlaylists(inpickle, fractrain, train_out, test_out):

    with open(inpickle, 'r') as f:
        P = pickle.load(f)['P']

    ids         = P.keys()
    random.shuffle(ids)

    n           = len(ids)
    numtrain    = int(n * fractrain)

    lists_train = getLists(P, ids[:numtrain])
    lists_test  = getLists(P, ids[numtrain:])

    with open(train_out, 'w') as f:
        pickle.dump(lists_train, f)

    with open(test_out, 'w') as f:
        pickle.dump(lists_test, f)

    pass

if __name__ == '__main__':
    splitPlaylists(sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4])
