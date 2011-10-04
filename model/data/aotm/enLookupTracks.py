#!/usr/bin/env python
'''
CREATED:2011-09-10 15:02:52 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Lookup AOTM playlist tracks => echo nest song ids

Usage:

./enLookupTracks.py en.ini artist_to_tracks.pickle OUTPUT.pickle

'''

import pyechonest, pyechonest.config, pyechonest.song, pyechonest.artist
import cPickle as pickle
import sys, time
import ConfigParser
import pprint


def lookupTracks(trackFile, outpickle):

    def loadOutput():
        h = {}
        try:
            with open(outpickle, 'r') as f:
                h = pickle.load(f)
        except:
            pass
        return h

    def dumpOutput(h):
        print '--- saving ---'
        with open(outpickle, 'w') as f:
            pickle.dump(h, f)

    idHash = loadOutput()

    with open(trackFile, 'r') as f:
        artist_to_tracks = pickle.load(f)

    for (i, (A, tracks)) in enumerate(artist_to_tracks.iteritems()):
        print '[%6d/%6d] %s' % (i, len(artist_to_tracks), A)

        if len(A) == 0:
            continue
        for track in tracks:
            print '\t[%s] - %s => ' % (A, track) ,
            key = (A, track)
            if key in idHash:
                print '%s [cached]' % idHash[key]
                continue
            idHash[key] = None
            try:
                results = pyechonest.song.search(title=track, artist=A, results=1)
                if len(results) > 0:
                    idHash[key] = results[0].id
                time.sleep(0.5)
            except:
                pass
            print idHash[key]
        if i % 50 == 0:
            dumpOutput(idHash)


    dumpOutput(idHash)


if __name__ == '__main__':
    # Initialize echo nest config
    cp = ConfigParser.SafeConfigParser()
    cp.read(sys.argv[1])
    pyechonest.config.ECHO_NEST_API_KEY = cp.get('echonest', 'api_key')
    pyechonest.config.TRACE_API_CALLS   = False

    lookupTracks(sys.argv[2], sys.argv[3])
