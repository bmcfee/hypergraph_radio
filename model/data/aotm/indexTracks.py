#!/usr/bin/env python

import sys, json
import glob
import cPickle as pickle
import pprint

def playlistGenerator(directory):

    for path in glob.glob('%s/*.json' % directory):
        with open(path, 'r') as f:
            playlist = json.load(f)
            if 'playlist' in playlist:
                yield playlist['playlist']


def loadTracksFromPlaylists(directory):

    artist_to_tracks = {}

    counter = 0
    for playlist in playlistGenerator(directory):
        for (artist, song) in playlist:
            artist  = artist.lower()
            song    = song.lower()
            if artist not in artist_to_tracks:
                artist_to_tracks[artist] = set()
            artist_to_tracks[artist].add(song)
        counter = counter + 1
        if counter % 1000 == 0:
            print '%6d...' % counter

    num_artists = len(artist_to_tracks)
    num_songs = 0

    for (artist, songs) in artist_to_tracks.iteritems():
        num_songs = num_songs + len(songs)

    print '%d artists, %d songs' % (num_artists, num_songs)
    return artist_to_tracks
    pass

if __name__ == '__main__':
    inDir       = sys.argv[1]
    outpickle   = sys.argv[2]

    artist_to_tracks = loadTracksFromPlaylists(inDir)
    with open(outpickle, 'w') as f:
        pickle.dump(artist_to_tracks, f)
    pass
