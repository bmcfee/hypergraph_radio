#!/usr/bin/env python
"""
CREATED:2011-10-11 09:51:39 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Construct optimized audio descriptors for MSD songs

Usage: ./extractAudioRepresentation.py songs.txt /data/1mil/ sql.ini output.pickle
"""

import sys, os, numpy
import cPickle as pickle

import pprint
import oursql
import ConfigParser

import clustering


def getTrackIDs(insongs, basedir):
    track_ids = {}
    insongs = set(insongs)

    with open(basedir + '/AdditionalFiles/unique_tracks.txt', 'r') as f:
        for line in f:
            (t_id, s_id, a, t) = line.strip().split('<SEP>', 4)
            if s_id in insongs:
                track_ids[t_id] = s_id

    return track_ids



def crunchData(song_list, basedir, dbc, outfile):


    # Step 1: load filenames
    with open(song_list, 'r') as f:
        song_ids = [x.strip() for x in f.readlines()]

    # Step 2: map track ids to song ids
    track_ids = getTrackIDs(song_ids, basedir)

    # Step 3: get audio data for each track
    data = clustering.FeatureMap()

    with dbc as cursor:
        cursor.execute('''SELECT echonest_id, data FROM Track''')
        counter = 0
        for (track, blob) in cursor:
            if track in track_ids and track_ids[track] not in data:
                data[track_ids[track]] = pickle.loads(blob)
                counter = counter + 1
                print '%6d/%6d %s' % (counter, len(song_ids), track_ids[track])

    with open(outfile, 'w') as f:
        pickle.dump({'X': data}, f)

    pass

if __name__ == '__main__':
    '''
    Usage: ./extractAudioRepresentation.py songs.txt /data/1mil/ sql.ini output.pickle
    '''
    config = ConfigParser.SafeConfigParser()
    config.read(sys.argv[3])

    with oursql.connect(    host    =config.get(    'mysql', 'host'), 
                            user    =config.get(    'mysql', 'username'),
                            passwd  =config.get(    'mysql', 'password'),
                            port    =config.getint( 'mysql', 'port'),
                            db      =config.get(    'mysql', 'database')) as dbc:
        crunchData(sys.argv[1], sys.argv[2], dbc, sys.argv[4])
    pass
