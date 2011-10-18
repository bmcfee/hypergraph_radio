#!/usr/bin/env python
'''
CREATED:2011-10-11 11:05:27 by Brian McFee <bmcfee@cs.ucsd.edu>

Get just the playlists we care about, indexed by mix_id

Usage:

./getPlaylistSet.py output.pickle PLAYLIST1.pickle PLAYLIST2.pickle ...


Output pickle contains hash:
    playlists: hash mix_id => list of playlists
    songs:  set of song_ids
'''

import sys
import cPickle as pickle

MIN_LENGTH = 3

CATEGORIES = [u'Alternating DJ', u'Ambient', u'Avant Garde', u'Blues', u'Break Up', u'Classical', u'Country', u'Cover', u'Dance/House', u'Depression', u'Drum & Bass', u'Drums', u'Drums and Bass', u'Electronic Music', u'Exercise', u'Experimental', u'Folk', u'Goth', u'Hardcore', u'Hip', u'Hip Hop', u'Indie', u'Indie Rock', u'Industrial', u'Jazz', u'Microsound', u'Mixed', u'Mixed Genre', u'Narrative', u'Punk', u'Reggae', u'Religious/Spiritual', u'Rhythm and Blues', u'Road Trip', u'Rock', u'Rock/Pop', u'Romantic', u'Single Artist', u'Skate/Thrash', u'Sleep', u'Techno', u'Theme', u'World Music']

def loadlist(inpickle):
    X = []
    with open(inpickle, 'r') as f:
        X = pickle.load(f)
    return X

def cleanGenerator(l):
    def cleanlist(p):
        q = [p[0]]
        for (i, s) in enumerate(p[1:]):
            if s == q[-1]:
                yield q
                q = []
            q.append(s)
        yield q
        pass

    for p in l:
        for q in cleanlist(p):
            yield q
    pass



def getPlaylistSet(output, inpickles):

    P = []
    for x in inpickles:
        P.extend(loadlist(x))

    Q           = {}

    for C in CATEGORIES:
        Q[C] = {'P': {}, 'songs': set()}
        pass

    for l in P:
        C = l['category']

        new_lists = []
        for sublist in cleanGenerator(l['filtered_lists']):
            if len(sublist) >= MIN_LENGTH:
                new_lists.append(sublist)
                Q[C]['songs'].update(sublist)
        if len(new_lists) > 0:
            Q[C]['P'][l['mix_id']] = new_lists
        pass

    for (C, P) in Q.iteritems():
        C = C.replace('/', '-')
        C = C.replace('&', 'and')
        with open('%s_%s.pickle' % (output, C), 'w') as f:
            pickle.dump(P, f)
        pass
    pass

if __name__ == '__main__':
    getPlaylistSet(sys.argv[1], sys.argv[2:])
    pass
