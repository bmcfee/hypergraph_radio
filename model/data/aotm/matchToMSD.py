#!/usr/bin/env python

'''
CREATED:2011-10-04 15:05:28 by Brian McFee <bmcfee@cs.ucsd.edu>

Matches tracks to MSD by echo nest id

Usage:

./matchToMSD.py aotm_song_ids.pickle /path/to/MSD/AdditionalFiles/unique_tracks.txt filtered_output_set.pickle
'''

import cPickle as pickle
import sys


def loadSongs(inpickle):
    
    X = {}
    with open(inpickle, 'r') as f:
        X = pickle.load(f)
    return X
    pass

def loadMSD(track_file):

    song_ids = set()
    with open(track_file, 'r') as f:
        for line in f:
            (track_id, song_id, artist, title) = line.strip().split('<SEP>', 4)
            song_ids.add(song_id)

    return song_ids
    pass

def matchToMSD(inpickle, unique_track_file, outpickle):

    songsToSONG_ID  = loadSongs(inpickle)
    msd_tracks      = loadMSD(unique_track_file)

    matched_tracks  = {}
    unique_match = set()
    for (u,v) in songsToSONG_ID.iteritems():
        if v in msd_tracks:
            matched_tracks[u] = v
            unique_match.add(v)

    with open(outpickle, 'w') as f:
        pickle.dump(matched_tracks, f)
    
    print '%d matched tracks' % len(matched_tracks)
    print '%d unique tracks' % len(unique_match)
    pass

if __name__ == '__main__':
    matchToMSD(sys.argv[1], sys.argv[2], sys.argv[3])
    pass
