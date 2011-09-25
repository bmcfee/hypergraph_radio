import whoosh, whoosh.index, whoosh.qparser

class Root(object):

    def __init__(self, indexPath):
        self.index  = whoosh.index.open_dir(indexPath)
        self.parser = whoosh.qparser.MultifieldParser(['title', 'artist', 'release', 'terms'], self.index.schema)
        pass


    def search(self, querystring):
        if querystring is None:
            return 

        with self.index.searcher() as search:
            results = search.search(self.parser.parse(unicode(querystring)), limit=10)
            output = []
            for r in results:
                output.append({     'title':    r['title'],
                                    'artist':   r['artist'],
                                    'song_id':  r['song_id'],
                                    'release':  r['release'] })

            return output
        pass


    def tags(self, query):

        with self.index.searcher() as search:
            results = search.document(song_id=query)
            if results is None:
                return
            else:
                return results['terms'].split(',')
        pass


    def artist(self, EN, query):

        with self.index.searcher() as search:
            results = search.document(song_id=query)
            if results is None:
                return

            artist_id   = results['artist_id']
            images      = EN.images(artist_id)
            biography   = EN.bio(artist_id)

            return {'image': images, 'bio': biography, 'song_id': query, 'artist_id': artist_id}
        pass

