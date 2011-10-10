#!/usr/bin/env python
"""
CREATED:2011-03-16 10:35:08 by Brian McFee <bmcfee@cs.ucsd.edu>

Load descriptors for points in a training/validation/test fold

Usage: ./loadFoldTags.py /path/to/train_data /path/to/MillionSongSubset
"""

import sys, os, numpy

import pprint
import sqlite3


def getTagVocab(dbc):

    cur = dbc.cursor()
    cur.execute('''SELECT term FROM terms''')

    vocab = {}
    for (i, (term,)) in enumerate(cur):
        vocab[term] = i
    return vocab

def getTagVector(dbc, vocab, artist_id):

    vector = numpy.zeros(len(vocab))

    cur = dbc.cursor()
    cur.execute('''SELECT term FROM artist_term WHERE artist_id = ?''', (artist_id,))
    for (term,) in cur:
        vector[vocab[term]] = 1

    return vector

def getArtistIDs(filenames, basedir):
    
    artistList = []
    with sqlite3.connect(basedir + '/AdditionalFiles/subset_track_metadata.db') as dbc:
        cur = dbc.cursor()

        for name in filenames:
            cur.execute('''SELECT artist_id FROM songs WHERE track_id = ?''', (name[6:-3],))
            (artist_id,) = cur.fetchone()
            artistList.append(artist_id)

    return artistList


def crunchData(infile, basedir, outfile, dbc):

    # Step 1: load tag vocabulary
    vocab = getTagVocab(dbc)

    # Step 2: load filenames
    with open(infile, 'r') as f:
        inputFiles = [x.strip() for x in f.readlines()]

    # Step 3: map filenames to artist ids
    artists = getArtistIDs(inputFiles, basedir)

    # Step 4: get tags for each artist
    data = len(inputFiles) * [None]
    for (i, f) in enumerate(inputFiles):
        print '%5d/%5d %s' % (i, len(inputFiles), f)
#         data[i] = numpy.loadtxt(basedir + '/data/' + f + '-vq-full-01.csv.gz', delimiter=',')
        data[i] = getTagVector(dbc, vocab, artists[i])
    numpy.savetxt(outfile, numpy.array(data), fmt='%1d', delimiter=',')

if __name__ == '__main__':
    infile = sys.argv[1]
    outfile = sys.argv[1] + '_vector'
    basedir = sys.argv[2]

    with sqlite3.connect(basedir + '/AdditionalFiles/subset_artist_term.db') as dbc:
        crunchData(infile, basedir, outfile, dbc)
