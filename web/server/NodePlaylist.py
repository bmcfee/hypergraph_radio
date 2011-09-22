import cPickle as pickle
import random

class Root(object):
    def __init__(self, songMeta, rdioMap, model):
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

    def sample(self, before, after, not_list):

        if before is None and after is None:
            return []

        # TODO:   2011-09-20 12:59:44 by Brian McFee <bmcfee@cs.ucsd.edu>
        # this is where markov smarts goes  

        if before in self.model:
            S = self.model[before]
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
