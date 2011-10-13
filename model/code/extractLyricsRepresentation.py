#!/usr/bin/env python
'''
CREATED:2011-10-12 18:48:34 by Brian McFee <bmcfee@cs.ucsd.edu>

Import VW LDA output to a featuremap

Usage:

./extractLyricsRepresentation.py playlistSet.pickle /path/to/vw_output featuremap_lyrics.pickle

'''

import sys, os, numpy
import cPickle as pickle
import clustering


def extractLyrics(playlistFile, vwfile, outfile):
    
    with open(playlistFile, 'r') as f:
        mysongs = pickle.load(f)['songs']

    data = clustering.FeatureMap()

    with open(vwfile, 'r') as f:
        for line in f:
            features = line.strip().split()
            song_id = features[-1]
            if song_id not in mysongs:
                continue
            v = numpy.array(map(float, features[:-1]))
            data[song_id] = (v / numpy.sum(v))**0.5
            pass

    print 'Imported %d songs' % len(data)
    with open(outfile, 'w') as f:
        pickle.dump({'X': data}, f)
    pass

if __name__ == '__main__':
    extractLyrics(sys.argv[1], sys.argv[2], sys.argv[3])
    pass
