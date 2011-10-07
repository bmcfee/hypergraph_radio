#!/usr/bin/env python
'''
CREATED:2011-10-04 19:38:47 by Brian McFee <bmcfee@cs.ucsd.edu>

Use a whoosh fulltext index to filter playlist data down to MSD.

In general, each playlist will now be a collection of contiguous playlists.

Usage:
./fullTextPlaylistIndex.py /path/to/playlists /path/to/text_index filtered_playlists.pickle
'''

import cPickle as pickle, json
import sys, os, glob
import pprint

import whoosh, whoosh.index, whoosh.qparser

def playlistGenerator(directory):

    for path in glob.glob('%s/*.json' % directory):
        with open(path, 'r') as f:
            P = json.load(f)
            if 'playlist' in P:
                yield P
    pass


def splitPlaylists(S):

    q = []
    for x in S:
        if x is not None:
            q.append(x)
        elif len(q) > 0:
                yield q
                q = []
    if len(q) > 0:
        yield q

def filterThisPlaylist(P, searcher, qa, qt):

    # First, map the playlist to a sequence of song ids or nones
    songs = []
    for (artist, song) in P['playlist']:
        results = searcher.search(qa.parse(artist) & qt.parse(song), limit=1)
        if len(results) > 0:
            songs.append(results[0]['song_id'])
        else:
            songs.append(None)
    # Now, split the sequence by Nones
    P['filtered_lists'] = [x for x in splitPlaylists(songs)]
    return P


def filterPlaylists(playlist_dir, index_dir, filterpickle):
    
    filtered_playlists = []

    index = whoosh.index.open_dir(index_dir)

    with index.searcher() as searcher:
        qa = whoosh.qparser.QueryParser('artist', index.schema)
        qt = whoosh.qparser.QueryParser('title', index.schema)
        for (i, P) in enumerate(playlistGenerator(playlist_dir)):
            filtered_playlists.append(filterThisPlaylist(P, searcher, qa, qt))
            print '%6d' % i

    with open(filterpickle, 'w') as f:
        pickle.dump(filtered_playlists, f)

    print '%d playlists' % len(filtered_playlists)
    pass



if __name__ == '__main__':
    filterPlaylists(sys.argv[1], sys.argv[2], sys.argv[3])
    pass
