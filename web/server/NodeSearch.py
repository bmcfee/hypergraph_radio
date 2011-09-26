import whoosh, whoosh.index, whoosh.qparser
import cPickle as pickle
import random

class Root(object):

    def __init__(self, indexPath, songMeta, rdioMap, model):
        self.index  = whoosh.index.open_dir(indexPath)
        self.parser = whoosh.qparser.MultifieldParser(['title', 'artist', 'release', 'terms'], self.index.schema)
        
        self.termlist  = []
        with self.index.reader() as reader:
            for term in reader.lexicon('terms'):
                self.termlist.append(term)

        self.songToRdio = {}
        with open(rdioMap, 'r') as f:
            self.songToRdio = pickle.load(f)

        self.songMeta = {}
        with open(songMeta, 'r') as f:
            self.songMeta = pickle.load(f)

        self.model = {}
        with open(model, 'r') as f:
            self.model = pickle.load(f)
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

    #---#


    def sample(self, before, after, not_list, tag_filter):

        if before is None and after is None:
            return []

        # TODO:   2011-09-20 12:59:44 by Brian McFee <bmcfee@cs.ucsd.edu>
        # this is where markov smarts goes  

        if before in self.model:
            S = self.model[before]
            if len(tag_filter) > 0:
                # TODO:   2011-09-26 11:49:33 by Brian McFee <bmcfee@cs.ucsd.edu>
                # put tag filter in here
                # use whoosh queries to do it
                pass
            while True:
                if len(S) == 0:
                    break
                x = random.choice(S)
                if x not in not_list:
                    return [self.package(x)]
                S.remove(x)

            return [self.package(random.choice(S))]

        return [self.package('SOITXNB12A8C144ECD')]

    def package(self, song_id):
        S = {   'song_id':  song_id, 
                'rdio_id':  self.songToRdio[song_id],
                'artist':   unicode(self.songMeta[song_id]['artist'], 'utf-8', errors='replace'),
                'title':    unicode(self.songMeta[song_id]['title'], 'utf-8', errors='replace') }
        return S

    def queue(self, qid):
        if qid in self.songToRdio and self.songToRdio[qid] is not None:
            return [self.package(qid)]
        else:
            return [self.package('SOCWJDB12A58A776AF')]
