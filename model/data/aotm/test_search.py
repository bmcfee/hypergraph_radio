#!/usr/bin/env python

import whoosh, whoosh.index, whoosh.qparser
import sys
import pprint

if __name__ == '__main__':
    
    index = whoosh.index.open_dir(sys.argv[1])

    with index.searcher() as search:
        q = whoosh.qparser.MultifieldParser(['title', 'artist'], index.schema).parse(unicode(' '.join(sys.argv[2:])))
        results = search.search(q, terms=True)
        for r in results:
            pprint.pprint(r)
            pprint.pprint(r.matched_terms())
            print '---'
