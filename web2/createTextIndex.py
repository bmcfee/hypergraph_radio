#!/usr/bin/env python
'''
CREATED:2012-04-22 15:32:49 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Usage:

./createTextIndex.py text_index_directory radio.db artist_terms.db


'''

import sys, os
import sqlite3

import whoosh, whoosh.fields, whoosh.index, whoosh.analysis
from whoosh.support.charset import accent_map


def createIndexWriter(indexPath):

    if not os.path.exists(indexPath):
        os.mkdir(indexPath)
        pass

    A = whoosh.analysis.StemmingAnalyzer() | whoosh.analysis.CharsetFilter(accent_map)

    Schema = whoosh.fields.Schema(  song_id     =   whoosh.fields.ID(stored=True),
                                    artist_id   =   whoosh.fields.STORED,
                                    artist      =   whoosh.fields.TEXT(stored=True, field_boost=8.0, analyzer=A),
                                    title       =   whoosh.fields.TEXT(stored=True, field_boost=4.0, analyzer=A),
                                    terms       =   whoosh.fields.KEYWORD(stored=True, scorable=True, commas=True))

    index = whoosh.index.create_in(indexPath, Schema)
    return index.writer()

def getArtistTerms(dbc, artist_id):
    cur = dbc.cursor()

    cur.execute('''SELECT term FROM artist_term WHERE artist_id = ?''', (artist_id,))
    
    return [unicode(t) for (t,) in cur]


def createIndex(indexPath, dbc_artist, dbc_radio):
    
    writer = createIndexWriter(indexPath)

    cur = dbc_radio.cursor()

    cur.execute('''     SELECT      Song.id, Song.title, Artist.id, Artist.name 
                        FROM        Song INNER JOIN Artist 
                        ON          Song.artist_id = Artist.id''')

    for (song_id, song_title, artist_id, artist_name) in cur:
        artist_terms    = u','.join(getArtistTerms(dbc_artist, artist_id))
        writer.add_document(    song_id     = song_id,
                                artist_id   = artist_id,
                                title       = song_title,
                                artist      = artist_name,
                                terms       = artist_terms)

        pass
    writer.commit()
    pass

if __name__ == '__main__':
    # ./createTextIndex.py text_index_directory radio.db artist_terms.db
    with sqlite3.connect(sys.argv[2]) as dbc_radio:
        with sqlite3.connect(sys.argv[3]) as dbc_artist:
            createIndex(sys.argv[1], dbc_artist, dbc_radio)
            pass
        pass
    pass

