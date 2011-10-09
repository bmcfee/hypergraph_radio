#!/usr/bin/env python
"""
CREATED:2011-10-09 12:32:41 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Construct optimized tag descriptors for MSD songs

Usage: ./extractTagRepresentation.py tag_metric.pickle songs.txt /1mil/ output.pickle
"""

import sys, os, numpy

import pprint
import sqlite3



def getTagVector(dbc, vocab, artist_id):

    vector = numpy.zeros(len(vocab))

    cur = dbc.cursor()
    cur.execute('''SELECT term FROM artist_term WHERE artist_id = ?''', (artist_id,))
    for (term,) in cur:
        if term in vocab:
            vector[vocab[term]] = 1

    return vector

def getArtistIDs(insongs, basedir):
    
    artistList = {}
    with sqlite3.connect(basedir + '/AdditionalFiles/subset_track_metadata.db') as dbc:
        cur = dbc.cursor()

        for song_id in insongs:
            cur.execute('''SELECT artist_id FROM songs WHERE song_id = ?''', (song_id,))
            (artist_id,) = cur.fetchone()
            artistList[song_id] = artist_id

    return artistList


def crunchData(parameters, song_list, basedir, outfile, dbc):

    # Step 1: load tag vocabulary
    with open(parameters, 'r') as f:
        P = pickle.load(f)

    # Step 2: load filenames
    with open(song_list, 'r') as f:
        song_ids = [x.strip() for x in f.readlines()]

    # Step 3: map filenames to artist ids
    artists = getArtistIDs(song_ids, basedir)

    # Step 4: get tags for each artist
    data = len(song_ids) * [None]
    for (i, s) in enumerate(song_ids):
        print '%6d/%6d %s' % (i, len(song_ids), s)
        data[i] = P['L'] * getTagVector(dbc, P['vocab'], artists[s])

    with open(outfile, 'w') as f:
        pickle.dump({'data': data, 'song_ids': song_ids, 'artist_ids': [artists[x] for x in song_ids]}, f)

    pass

if __name__ == '__main__':
    '''
    Usage: ./extractTagRepresentation.py tag_metric.pickle songs.txt /1mil/ output.pickle
    '''

    with sqlite3.connect(sys.argv[3] + '/AdditionalFiles/artist_term.db') as dbc:
        crunchData(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], dbc)
    pass
