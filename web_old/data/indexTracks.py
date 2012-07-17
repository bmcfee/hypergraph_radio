#!/usr/bin/env python
'''
CREATED:2011-09-18 15:01:23 by Brian McFee <bmcfee@cs.ucsd.edu>

Usage:

./indexTracks.py /path/to/track_metadata.db /path/to/artist_terms.db /path/to/index_dir

'''

import sys, pprint, os
import sqlite3
import whoosh, whoosh.fields, whoosh.index



def getTerms(dbc, artist_id):
    cur = dbc.cursor()
    cur.execute('''SELECT term FROM artist_term WHERE artist_id = ?''', (artist_id,))

    res = []
    for (term) in cur:
        res.append(unicode(term[0]))
    return u','.join(res)
    pass


def createIndexWriter(indexPath):

    if not os.path.exists(indexPath):
        os.mkdir(indexPath)

    Schema = whoosh.fields.Schema(  song_id     =   whoosh.fields.ID(stored=True),
                                    title       =   whoosh.fields.TEXT(stored=True, field_boost=8.0),
                                    artist      =   whoosh.fields.TEXT(stored=True, field_boost=4.0),
                                    release     =   whoosh.fields.TEXT(stored=True, field_boost=2.0),
                                    terms       =   whoosh.fields.KEYWORD(stored=True, scorable=True, commas=True))

    index = whoosh.index.create_in(indexPath, Schema)

    return index.writer()
    pass


def createIndex(dbc_meta, dbc_terms, indexPath):

    cur = dbc_meta.cursor()

    cur.execute('''SELECT   song_id,
                            title,
                            artist_name,
                            artist_id,
                            release
                    FROM    songs''')

    writer = createIndexWriter(indexPath)

    for (s_id, track_title, artist_name, artist_id, release_name) in cur:
        term_array = getTerms(dbc_terms, artist_id)


        writer.add_document(song_id     =   s_id, 
                            title       =   track_title, 
                            artist      =   artist_name,
                            release     =   release_name,
                            terms       =   term_array)
    writer.commit()
    pass

if __name__ == '__main__':
    with sqlite3.connect(sys.argv[1]) as dbc_meta:
        with sqlite3.connect(sys.argv[2]) as dbc_terms:
            createIndex(dbc_meta, dbc_terms, sys.argv[3])
