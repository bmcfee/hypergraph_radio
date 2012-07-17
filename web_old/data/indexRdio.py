#!/usr/bin/env python
"""
CREATED:2011-09-18 18:00:37 by Brian McFee <bmcfee@cs.ucsd.edu>

Lookup Rdio ids for each echo nest track

Usage:

./indexRdio.py en.ini /path/to/unique_tracks.txt songToRdio.pickle
"""

import cPickle as pickle

import json

import sys, time
import urllib2

import ConfigParser

import pprint

def loadMapping(filename):

    with open(filename, 'r') as f:
        M = pickle.load(f)
        return M
    return {}

def lookupRdio(api_key, song_id):

    while True:
        try:
            f = urllib2.urlopen('http://developer.echonest.com/api/v4/song/profile?api_key=%s&format=json&id=%s&bucket=id:rdio-us-streaming' % (api_key, song_id))

            data = json.loads(f.read())['response']
    
            rdio_id = None

            if      'songs' in data and len(data['songs']) > 0  and u'foreign_ids' in data['songs'][0]  and len(data['songs'][0]['foreign_ids']) > 0:
                # Success.  Moving on...
                foreign_id  = data['songs'][0]['foreign_ids'][0]['foreign_id']
                rdio_id     = foreign_id[foreign_id.rfind(':')+1:]

            time.sleep(0.5)

            return rdio_id
        finally:
            time.sleep(0.5)
    pass

def saveMapping(M, filename):
    with open(filename, 'w') as f:
        pickle.dump(M, f)
    pass

def scanTracks(api_key, trackfile, mappingPickle):

    songToRdio = loadMapping(mappingPickle)

    counter = 0
    with open(trackfile, 'r') as f:
        for line in f:
            (track_id, song_id, artist, title) = line.strip().split('<SEP>', 4)
            counter += 1
            print '[%s] %s - %s' % (song_id, artist, title),
            if song_id in songToRdio:
                print ' => [%s] (cached)' % songToRdio[song_id]
            else:
                songToRdio[song_id] = lookupRdio(api_key, song_id)
                print ' => [%s]' % songToRdio[song_id]
                saveMapping(songToRdio, mappingPickle)
    pass




if __name__ == '__main__':
    cp = ConfigParser.SafeConfigParser()
    cp.read(sys.argv[1])

    scanTracks(cp.get('echonest', 'api_key'), sys.argv[2], sys.argv[3])
    pass
