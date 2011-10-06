#!/usr/bin/env python
'''
CREATED:2011-10-04 19:16:19 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Index the MSD (artist, title) tuples with whoosh

Usage:


./buildMSDtextIndex.py /path/to/unique_tracks.py /path/to/whoosh/index

'''

import sys, os
import cPickle as pickle
import whoosh, whoosh.fields, whoosh.index, whoosh.analysis
from whoosh.support.charset import accent_map


def createIndexWriter(indexPath):
    if not os.path.exists(indexPath):
        os.mkdir(indexPath)

    A = whoosh.analysis.FancyAnalyzer() | whoosh.analysis.CharsetFilter(accent_map)

    Schema = whoosh.fields.Schema(  song_id     = whoosh.fields.ID(stored=True),
                                    artist      = whoosh.fields.TEXT(stored=True, analyzer=A),
                                    title       = whoosh.fields.TEXT(stored=True, analyzer=A))

    index = whoosh.index.create_in(indexPath, Schema)
    return index.writer()
    pass

def parseTracks(trackfile):

    with open(trackfile, 'r') as f:
        for line in f:
            (track, song, artist, title) = map(lambda x: unicode(x, 'utf-8', errors='replace'), line.strip().split('<SEP>', 4))
            yield (song, artist, title)
    pass

def createIndex(trackfile, indexPath):
        
    writer = createIndexWriter(indexPath)

    for (i, (s, a, t)) in enumerate(parseTracks(trackfile)):

        writer.add_document(song_id     =   s,
                            artist      =   a,
                            title       =   t)
        if i % 1000 == 0:
            print '%6d...' % i
    writer.commit()
    pass

if __name__ == '__main__':
    createIndex(sys.argv[1], sys.argv[2])

