import whoosh, whoosh.index, whoosh.qparser
import cjson as json
import pprint

class Root(object):

    def __init__(self, indexPath):
        self.index  = whoosh.index.open_dir(indexPath)
        self.parser = whoosh.qparser.MultifieldParser(['title', 'artist', 'release', 'terms'], self.index.schema)

    def search(self, querystring):
        if querystring == '*':
            return json.encode([])

        with self.index.searcher() as search:
            results = search.search(self.parser.parse(unicode(querystring)), limit=10)
            output = []
            for r in results:
                output.append({     'title':    r['title'],
                                    'artist':   r['artist'],
                                    'song_id':  r['song_id'],
                                    'release':  r['release'] })

            return json.encode(output)
        pass
