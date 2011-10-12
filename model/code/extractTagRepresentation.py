#!/usr/bin/env python
"""
CREATED:2011-10-09 12:32:41 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Construct optimized tag descriptors for MSD songs

Usage: ./extractTagRepresentation.py tag_metric.pickle playlistSet.pickle /1mil/ output.pickle
"""

import sys, os, numpy
import cPickle as pickle

import pprint
import sqlite3

import clustering


def getTagVector(dbc, vocab, artist_id, L):

    vector = numpy.zeros(len(vocab))

    cur = dbc.cursor()
    cur.execute('''SELECT term FROM artist_term WHERE artist_id = ?''', (artist_id,))
    for (term,) in cur:
        if term in vocab:
            vector[vocab[term]] = 1

    return numpy.dot(L, vector)


def getArtistIDs(insongs, basedir):
    artistList = {}
    insongs = set(insongs)
    with sqlite3.connect(basedir + '/AdditionalFiles/track_metadata.db') as dbc:
        cur = dbc.cursor()
        cur.execute('''SELECT song_id, artist_id FROM songs''')
        for (song_id, artist_id) in cur:
            if song_id in insongs:
                artistList[song_id] = artist_id
    return artistList



def crunchData(parameters, song_pickle, basedir, outfile, dbc):

    # Step 1: load tag vocabulary
    with open(parameters, 'r') as f:
        P = pickle.load(f)

    # Step 2: load filenames
    with open(song_pickle, 'r') as f:
        song_ids = pickle.load(f)['songs']

    # Step 3: map filenames to artist ids
    artists = getArtistIDs(song_ids, basedir)

    # Step 4: get tags for each artist
    data = clustering.FeatureMap()
    for (i, s) in enumerate(song_ids):
        print '%6d/%6d %s' % (i, len(song_ids), s)
        data[s] = getTagVector(dbc, P['vocab'], artists[s], P['L'])

    with open(outfile, 'w') as f:
        pickle.dump({'X': data}, f)

    pass

if __name__ == '__main__':
    '''
    Usage: ./extractTagRepresentation.py tag_metric.pickle playlistSet.pickle /1mil/ output.pickle
    '''

    with sqlite3.connect(sys.argv[3] + '/AdditionalFiles/artist_term.db') as dbc:
        crunchData(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], dbc)
    pass
