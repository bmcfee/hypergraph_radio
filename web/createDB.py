#!/usr/bin/env python
'''
CREATED:2012-04-22 13:46:13 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Instantiate the MSD-RDIO hypergraph database

Usage:

./createDB.py NEW_DB.sqlite MODEL.pickle /path/to/1mil/AdditionalFiles


'''

import sys
import sqlite3
import cPickle as pickle
import hypergraph


def createSchema(dbc):
    cur = dbc.cursor()

    ###
    # Drop existing tables
    #

    for t in ['Song', 'Artist', 'Edge', 'Song_to_Edge', 'Model', 'Model_to_Edge']:
        cur.execute('DROP TABLE IF EXISTS %s' % t)
        pass
    cur.execute('''VACUUM''')

    ###
    # Create the new tables
    #
    cur.execute('''CREATE TABLE Song            (id TEXT PRIMARY KEY,       rdio_id TEXT, 
                                                                            artist_id TEXT, 
                                                                            title TEXT)''')
    cur.execute('''CREATE TABLE Artist          (id TEXT PRIMARY KEY,       name TEXT)''')
    cur.execute('''CREATE TABLE Edge            (id INTEGER PRIMARY KEY,    description TEXT)''')
    cur.execute('''CREATE TABLE Song_to_Edge    (song_id TEXT,              edge_id TEXT)''')
    cur.execute('''CREATE TABLE Model           (id INTEGER PRIMARY KEY,    name TEXT)''')
    cur.execute('''CREATE TABLE Model_to_Edge   (model_id INTEGER,          edge_id INTEGER, weight REAL)''')

    ###
    # Create index structures
    #
    cur.execute('''CREATE INDEX S2E_Song    ON Song_to_Edge     (song_id)''')
    cur.execute('''CREATE INDEX S2E_Edge    ON Song_to_Edge     (edge_id)''')
    cur.execute('''CREATE INDEX M2E_Model   ON Model_to_Edge    (model_id)''')

    pass


def getTrackMeta(dbc, tracks_to_rdio):

    cur = dbc.cursor()
    artists = {}
    songs   = {}
    cur.execute('''SELECT track_id, title, song_id, artist_id, artist_name FROM songs''')

    for (track_id, title, song_id, artist_id, artist_name) in cur:
        if track_id not in tracks_to_rdio:
            continue
        artists[artist_id]   = artist_name
        songs[song_id]      = (track_id, title, artist_id)
        pass
    return (artists, songs)

def importSongs(dbc, additionalFiles):

    # 1. build track => rdio id map
    tracks_to_rdio      = {}
    with open('%s/rdio_ids.txt' % additionalFiles, 'r') as f:
        for line in f:
            (tr_id, rdio_id) = line.strip().split('<SEP>', 2)
            tracks_to_rdio[tr_id] = rdio_id
            pass
        pass

    with sqlite3.connect('%s/track_metadata.db' % additionalFiles) as dbc_track:
        (artists, songs) = getTrackMeta(dbc_track, tracks_to_rdio)
        pass

    # 4. insert into artist table
    cur = dbc.cursor()
    cur.executemany('''INSERT INTO Artist (id, name) VALUES (?, ?)''', artists.iteritems())

    # 5. insert into song table

    def songIterator():
        for song_id in songs:
            (track_id, title, artist_id) = songs[song_id]
            rdio_id     = tracks_to_rdio[track_id]
            yield (song_id, rdio_id, artist_id, title)
        pass

    cur.executemany('''INSERT INTO Song (id, rdio_id, artist_id, title) VALUES (?, ?, ?, ?)''', songIterator())

    pass


def importEdges(dbc, modelFile):

    with open(modelFile, 'r') as f:
        G = pickle.load(f)['G']
        pass

    BAD_EDGES = set(['__UNIFORM'])

    def edgeLabelIterator():
        for l in G._Hypergraph__edge_to_label:
            if l in BAD_EDGES:
                continue
            yield (l,)
        pass

    cur = dbc.cursor()
    cur.executemany('''INSERT INTO Edge (description) VALUES (?)''', edgeLabelIterator())

    edgeIDs = {}
    cur.execute('''SELECT * FROM Edge''')
    for (edge_id, desc) in cur:
        edgeIDs[G._Hypergraph__label_to_edge[desc]] = edge_id
        pass

    def s2eIterator():
        for (edge, edge_id) in edgeIDs.iteritems():
            for song_id in G._Hypergraph__edge_set[edge]:
                yield (song_id, edge_id)

    cur.executemany('''INSERT INTO Song_to_Edge (song_id, edge_id) VALUES (?, ?)''', s2eIterator())

    pass


if __name__ == '__main__':
    with sqlite3.connect(sys.argv[1]) as dbc:
        createSchema(dbc)
        importSongs(dbc, sys.argv[3])
        importEdges(dbc, sys.argv[2])
        dbc.commit()
        pass

