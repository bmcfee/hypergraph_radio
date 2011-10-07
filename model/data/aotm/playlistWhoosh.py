#!/usr/bin/env python
'''
CREATED:2011-10-05 10:36:28 by Brian McFee <bmcfee@cs.ucsd.edu>

Use a whoosh fulltext index to filter playlist data down to MSD.

In general, each playlist will now be a collection of contiguous playlists.

Usage:
./playlistWhoosh.py playlist_pickle /path/to/text_index filtered_playlists.pickle
'''

import cPickle as pickle
import sys, os, glob
import pprint
import re

import whoosh, whoosh.index, whoosh.qparser

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


def processResults(results):
    '''
    Only count a match if it hits on both artist and title
    '''
    output = (None,)
    for r in results:
        if len(r.matched_terms()) < 2:
            continue
        output = (r['song_id'], r['artist'], r['title'])
        break
    return output


bkiller = re.compile('\(.*?\)|\[.*?\]|\{.*?\}')

def filterThisPlaylist(P, searcher, qa, qt):

    # First, map the playlist to a sequence of song ids or nones
    songs = []
    for (artist, song) in P['playlist']:
        song = bkiller.sub(' ', song).strip()
        artist = bkiller.sub(' ', artist).strip()
        if len(artist) == 0 or len(song) == 0:
            continue

        # Kill song title bits in brackets or parentheses

        q_artist    = qa.parse(artist)
        q_title     = qt.parse(song)
        if q_artist == whoosh.query.NullQuery() or q_title == whoosh.query.NullQuery():
            output = (None,)
        else:
            output = processResults(searcher.search(q_artist & q_title, terms=True))
        songs.append(output[0])
#         pprint.pprint((artist, song, output))
    # Now, split the sequence by Nones
    P['playlist'] = zip(P['playlist'], songs)
    P['filtered_lists'] = [x for x in splitPlaylists(songs)]
    return P


def filterPlaylists(playlist_pickle, index_dir, filterpickle):
    
    with open(playlist_pickle, 'r') as f:
        playlists = pickle.load(f)

    N = len(playlists)
    filtered_playlists = []

    index = whoosh.index.open_dir(index_dir)

    with index.searcher() as searcher:
        searcher.set_caching_policy(save=False)
        qa = whoosh.qparser.SimpleParser('artist', index.schema)
        qt = whoosh.qparser.SimpleParser('title', index.schema)
        
        for x in [qa, qt]:
            x.remove_plugin_class(whoosh.qparser.PlusMinusPlugin)

        for (i, P) in enumerate(playlists):
            filtered_playlists.append(filterThisPlaylist(P, searcher, qa, qt))
            if i % 10 == 0:
                print '%5d/%5d' % (i, N)
            if i > 20:
                break;

    with open(filterpickle, 'w') as f:
        pickle.dump(filtered_playlists, f)

    print '%d playlists' % len(filtered_playlists)
    pass



if __name__ == '__main__':
    filterPlaylists(sys.argv[1], sys.argv[2], sys.argv[3])
    pass
