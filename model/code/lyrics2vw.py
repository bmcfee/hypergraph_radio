#!/usr/bin/env python
'''
CREATED:2011-10-12 18:01:54 by Brian McFee <bmcfee@cs.ucsd.edu>

Extract MXM lyrics database and put into vw format

Usage:
./lyrics2vw.py /path/to/1mil vw_input.txt

'''

import sqlite3
import cPickle as pickle
import sys


def getTrackMap(msdpath):

    trackmap = {}
    with open(msdpath + '/AdditionalFiles/unique_tracks.txt', 'r') as f:
        for line in f:
            (track_id, song_id, artist, title) = line.strip().split('<SEP>', 4)
            trackmap[track_id] = song_id
            pass
    return trackmap


def getVocab(dbc):
    
    vocab = {}
    cur = dbc.cursor()
    cur.execute('''SELECT word FROM words''')

    for (i, (word,)) in enumerate(cur):
        vocab[word] = i
        pass
    return vocab

def getLyrics(dbc):
    
    cur = dbc.cursor()
    cur.execute('''SELECT track_id, word, count FROM lyrics ORDER BY track_id''')

    lyrics = {}
    prev_track_id = None
    for (track_id, word, count) in cur:
        if prev_track_id is None:
            prev_track_id = track_id

        if prev_track_id == track_id:
            lyrics[word] = count

        else:
            yield (prev_track_id, lyrics)
            prev_track_id = track_id
            lyrics = {word: count}
        pass
    yield (prev_track_id, lyrics)
    pass


def lyricsToVW(dbc, msdpath, output):
    
    trackToSongs    = getTrackMap(msdpath)
    vocab           = getVocab(dbc)

    print '%d words' % len(vocab)
    with open(output, 'w') as f:
        for (track_id, lyrics) in getLyrics(dbc):
            s = '1 %s|' % trackToSongs[track_id]
            for (word, count) in lyrics.iteritems():
                s += '%s:%d ' % (vocab[word], count)
                pass
            f.write(s + '\n')
            pass
    pass


if __name__ == '__main__':
    with sqlite3.connect(sys.argv[1] + '/AdditionalFiles/mxm_dataset.db') as dbc:
        lyricsToVW(dbc, sys.argv[1], sys.argv[2])
