import whoosh, whoosh.index, whoosh.qparser, whoosh.query
import random

class Search(object):
    
    def __init__(self, cfg):
        self.index  = whoosh.index.open_dir(cfg['text_index'])
        self.parser = whoosh.qparser.MultifieldParser(
                            ['title', 'artist', 'terms'], 
                            self.index.schema)
        pass

    def search(self, query):
        if query is None:
            return None

        output = []

        with self.index.searcher() as searcher:
            R = searcher.search(self.parser.parse(unicode(query)), limit=10)


            for res in R:
                output.append(  {   'title':    res['title'],
                                    'artist':   res['artist'],
                                    'song_id':  res['song_id']})
                pass
            pass

        return output
