#!/usr/bin/env python
'''
CREATED:2011-10-10 14:36:04 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Refines a clustering into k subclusters using a provided featuremap

Usage:

./refineClustering.py clustering.pickle featuremap.pickle k DESCRIPTION_STRING output_clustering.pickle
'''

import sys, os
import cPickle as pickle
import clustering


def refine(clustering_pickle, features_pickle, k, description, outpickle):

    print 'Loading clustering %s...' % clustering_pickle,
    with open(clustering_pickle, 'r') as f:
        clustering  = pickle.load(f)
    print ' done.'

    print 'Loading features %s...' % features_pickle,
    with open(features_pickle, 'r') as f:
        features    = pickle.load(f)
    print ' done.'

    print 'Refining each cluster into %d clusters...' % k
    C_new = clustering['C'].refine(k, features['X'])
    C_new.setDescription(description)

    print 'Saving %s...' % outpickle,
    with open(outpickle, 'w') as f:
        pickle.dump({'C': C_new}, f)
    print ' done!'
    pass

if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    refine(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5])
