#!/usr/bin/env python
'''
CREATED:2011-10-17 20:31:52 by Brian McFee <bmcfee@cs.ucsd.edu>

Refine a spill tree by feature partitioning

Usage:

./refineTree.py /path/tree_uniform /path/featuremap Label_pattern /path/to/output_pattern SPLIT1 [SPLIT2 ...]
'''

import sys, os
import cPickle as pickle
import clustering

def refineTrees(base_tree_P, feature_P, pattern_label, pattern_out, levels):

    with open(base_tree_P, 'r') as f:
        C = pickle.load(f)['C']

    with open(feature_P, 'r') as f:
        X = pickle.load(f)['X']

    for i in range(1, max(levels)+1):
        print 'Refinement %03d\n\t' % i,
        C = C.refine(X=X)
        C.setDescription(pattern_label % i)
        if i in levels:
            print 'Saving... ',
            with open(pattern_out % i, 'w') as f:
                pickle.dump({'C': C}, f)
            print 'done'
            pass
        pass


if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)    
    refineTrees(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], set(map(int, sys.argv[5:])))
    pass
