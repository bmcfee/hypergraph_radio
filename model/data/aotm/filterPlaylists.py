#!/usr/bin/env python
'''
CREATED:2011-10-04 15:31:54 by Brian McFee <bmcfee@cs.ucsd.edu>

Filter the playlist set down to just tracks contained in MSD.

In general, each playlist will now be a collection of contiguous playlists.

Usage:
./filterPlaylists matched_MSD_songs.pickle /path/to/playlists filtered_playlists.pickle
'''

import cPickle as pickle, json
import sys, os, glob
import pprint

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

def filterThisPlaylist(P, songmap):

    # First, map the playlist to a sequence of song ids or nones
    songs = []
    for (artist, song) in P['playlist']:
        artist  = artist.lower()
        song    = song.lower()
        if (artist, song) in songmap:
            songs.append(songmap[(artist, song)])
        else:
            songs.append(None)

    # Now, split the sequence by Nones
    P['filtered_lists'] = [x for x in splitPlaylists(songs)]
    return P


def filterPlaylists(matchpickle, playlist_dir, filterpickle):
    
    songmap = {}
    with open(matchpickle, 'r') as f:
        songmap = pickle.load(f)

    filtered_playlists = []

    for P in playlistGenerator(playlist_dir):
        filtered_playlists.append(filterThisPlaylist(P, songmap))

    with open(filterpickle, 'w') as f:
        pickle.dump(filtered_playlists, f)

    print '%d playlists' % len(filtered_playlists)
    pass



if __name__ == '__main__':
    filterPlaylists(sys.argv[1], sys.argv[2], sys.argv[3])
    pass
