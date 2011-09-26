import whoosh, whoosh.index, whoosh.qparser

class Root(object):

    def __init__(self, indexPath):
        self.index  = whoosh.index.open_dir(indexPath)
        self.parser = whoosh.qparser.MultifieldParser(['title', 'artist', 'release', 'terms'], self.index.schema)
        self.termlist  = []
        with self.index.reader() as reader:
            for term in reader.lexicon('terms'):
                self.termlist.append(term)
        pass

    def terms(self):
        return self.termlist

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
            docnum = search.document_number(song_id=query)
            if docnum is None:
                return
            else:
                kw = search.key_terms([docnum], 'terms', numterms=10)
                return [u for (u,v) in kw]
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

