"""Interface to whoosh full-text search"""

import whoosh, whoosh.index, whoosh.qparser, whoosh.query

class Search(object):
    """Interface to whoosh full-text search. 
    
    The class wrapper provides a convenient store for the parser object and whoosh
    connector.
    """
    
    def __init__(self, cfg):
        """Search object constructor:

        Arguments:
            cfg --  (dict) from server.ini config parse
                    cfg['text_index'] provides the path to the whoosh DB
        """
        self.index  = whoosh.index.open_dir(cfg['text_index'])
        self.parser = whoosh.qparser.MultifieldParser(
                            ['title', 'artist', 'terms'], 
                            self.index.schema)

    def search(self, query):
        """Full-text search for titles, artists, terms

        Arguments:
            query   -- (str)    the query string
        
        Returns:
            hits    -- list of dicts
                
                hits[k] = { 'title':   song title, 
                            'artist':  artist name, 
                            'song_id': song identifier}

            or None if the query is empty
        """

        if query is None:
            return None

        with self.index.searcher() as searcher:
            hits = []
            for result in searcher.search(self.parser.parse(unicode(query)), 
                                       limit=10):
                hits.append({'title':    result['title'],
                             'artist':   result['artist'],
                             'song_id':  result['song_id']})
        return hits
