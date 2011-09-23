#!/usr/bin/env python
'''
CREATED:2011-09-20 14:59:32 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Extract feature vectors from the sql database

Usage:

./sqlExtractVectors.py sql.ini valid_rdio.pickle output_vectors.pickle

'''

import sys
import oursql, ConfigParser
import numpy
import cPickle as pickle


def extractVectors(config, inputPickle, outputPickle):

    with open(inputPickle, 'r') as f:
        song_to_track = pickle.load(f)

    songs   = []
    vectors = []

    with oursql.connect(    host    =config.get(    'mysql', 'host'), 
                            user    =config.get(    'mysql', 'username'),
                            passwd  =config.get(    'mysql', 'password'),
                            port    =config.getint( 'mysql', 'port'),
                            db      =config.get(    'mysql', 'database')) as conn:
        with conn as cursor:
            
            for (song, track) in song_to_track.iteritems():
                cursor.execute('''SELECT data FROM Track WHERE echonest_id = ? LIMIT 1''', (track,))
                for (data,) in cursor:
                    songs.append(song)
                    vectors.append(pickle.loads(data))

    with open(outputPickle, 'w') as f:
        pickle.dump({'songs': songs, 'vectors': vectors}, f)

    pass
if __name__ == '__main__':

    config = ConfigParser.SafeConfigParser()
    config.read(sys.argv[1])

    extractVectors(config, sys.argv[2], sys.argv[3])
    pass
