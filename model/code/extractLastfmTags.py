#!/usr/bin/env python
'''
CREATED:2011-11-02 17:13:02 by Brian McFee <bmcfee@cs.ucsd.edu>

Construct a taghopper binary tag vector feature map from last.fm MSD tags

Usage: ./extractLastfmTags.py playlistSet.pickle /1mil/ output.pickle

'''

import sys, os, numpy
import cPickle as pickle
import pprint
import sqlite3
import taghopper


BACKGROUND_WORD = '__MECHA DERP ZILLA__'

def getVocab(dbc):
    vocab = [BACKGROUND_WORD]
    cur = dbc.cursor()
    cur.execute('''SELECT tag FROM tags''')
    for (term,) in cur:
        vocab.append(term)
        pass
    return vocab

def getTrackIds(song_ids, basedir):

    track_ids = {}

    with open('%s/AdditionalFiles/unique_tracks.txt' % basedir, 'r') as f:
        for line in f:
            (t, s, artist, title) = line.strip().split('<SEP>', 4)
            if s in song_ids:
                track_ids[s] = t
            pass

    return track_ids

def getTrackRows(dbc, track_ids):

    cur         = dbc.cursor()
    tid         = {}
    cur.execute('''SELECT tid FROM tids''')
    for (i, (track,)) in enumerate(cur, 1):
        tid[track] = i
        pass
    return tid


def getTags(dbc, F, tid, track_id):
    cur = dbc.cursor()

    terms = [BACKGROUND_WORD]
    if track_id in tid:
        cur.execute('''SELECT tag FROM tid_tag WHERE tid = ? ORDER BY val DESC limit 20''', (tid[track_id],))
        for (tag,) in cur:
            terms.append(F.tagnum(tag))
    return terms


def crunchData(dbc, basedir, p_playlist, p_output):

    print 'Loading songs'
    with open(p_playlist, 'r') as f:
        song_ids = pickle.load(f)['songs']
        pass

    print 'Mapping to track ids'
    track_ids   = getTrackIds(song_ids, basedir)
    print 'Mapping to row numbers'
    tid         = getTrackRows(dbc, track_ids)

    print 'Building vocabulary'
    vocab       = getVocab(dbc)
    print 'Constructing featuremap'
    data        = taghopper.FeatureMap(vocab)


    print 'Loading data'
    for (i, s) in enumerate(song_ids):
        print '%6d/%6d %s' % (i, len(song_ids), s)
        data[s] = getTags(dbc, data, tid, track_ids[s])
        pass

    print 'Compressing index'
    data = data.condense()

    print 'Saving'
    with open(p_output, 'w') as f:
        pickle.dump({'X': data}, f)
        pass
    print 'Done'
    pass

if __name__ == '__main__':
    with sqlite3.connect(sys.argv[2] + '/AdditionalFiles/lastfm_tags.db') as dbc:
        crunchData(dbc, sys.argv[2], sys.argv[1], sys.argv[3])
    pass
