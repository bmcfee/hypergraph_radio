import whoosh, whoosh.index, whoosh.qparser, whoosh.query
import cPickle as pickle
import random
import pprint

class Root(object):

    def __init__(self, indexPath, songMeta, rdioMap, model):
        '''
            indexPath:  path to the whoosh index directory
            songMeta:   path to the song metadata pickle
            rdioMap:    path to the song->rdio_id pickle
            model:      path to the playlist model pickle
        '''
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


    def all_terms(self):
        '''
            return all artist terms in the index
        '''
        return self.termlist

    def search(self, querystring):
        '''
            whoosh search for tracks
        '''
        if querystring is None:
            return 

        with self.index.searcher() as searcher:
            results = searcher.search(self.parser.parse(unicode(querystring)), limit=10)
            output = []
            for r in results:
                output.append({     'title':    r['title'],
                                    'artist':   r['artist'],
                                    'song_id':  r['song_id'],
                                    'release':  r['release'] })

            return output
        pass


    def tags(self, query):
        '''
            get the artist terms for a specific song
        '''
        with self.index.searcher() as searcher:
            docnum = searcher.document_number(song_id=query)
            if docnum is None:
                return
            else:
                kw = searcher.key_terms([docnum], 'terms', numterms=10)
                return [u for (u,v) in kw]
        pass


    def artist(self, EN, query):
        '''
            get artist info for a given song
        '''
        with self.index.searcher() as searcher:
            results = searcher.document(song_id=query)
            if results is None:
                return

            artist_id   = results['artist_id']
            images      = EN.images(artist_id)
            biography   = EN.bio(artist_id)

            return {'image': images, 'bio': biography, 'song_id': query, 'artist_id': artist_id}
        pass

    #---#


    def sample(self, before, after, not_list, tag_filter):
        '''
            sample from the playlist model
        '''
        # TODO:   2011-09-20 12:59:44 by Brian McFee <bmcfee@cs.ucsd.edu>
        # this is where markov smarts goes  

        #   search logic:
        #       song_id in self.model[before]
        #       song_id not in not_list
        #       matching tag_filter


        # Build the neighbor part of the query
        q_neighbor = whoosh.query.NullQuery
        if before in self.model:
            for n in self.model[before]:
                q_neighbor |= whoosh.query.Term("song_id", n)
            
        # Build the exlusion list
        q_notlist = whoosh.query.NullQuery
        for x in not_list:
            q_notlist |= whoosh.query.Term("song_id", x)

        # Build the tag list
        q_taglist = whoosh.query.NullQuery
        for t in tag_filter:
            q_taglist &= whoosh.query.Term("terms", t)

        query = (q_neighbor - q_notlist) & q_taglist

        with self.index.searcher() as searcher:
            results = searcher.search(query)
            
            ids = [r['song_id'] for r in results]
            if len(ids) > 0:
                return [self.package(random.choice(ids))]
            pass

        # if we fail, return some garbage
        return [self.package('SOITXNB12A8C144ECD')]


    def package(self, song_id):
        '''
            package a song with ids and metadata
        '''
        S = {   'song_id':  song_id, 
                'rdio_id':  self.songToRdio[song_id],
                'artist':   unicode(self.songMeta[song_id]['artist'], 'utf-8', errors='replace'),
                'title':    unicode(self.songMeta[song_id]['title'], 'utf-8', errors='replace') }
        return S


    def queue(self, qid):
        '''
            wrapper for song access
        '''
        if qid in self.songToRdio and self.songToRdio[qid] is not None:
            return [self.package(qid)]
        else:
            return [self.package('SOCWJDB12A58A776AF')]
