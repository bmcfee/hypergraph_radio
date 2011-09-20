import cjson as json
import cPickle as pickle

class Root(object):
    def __init__(self, songMeta, rdioMap):
        self.songToRdio = {}
        with open(rdioMap, 'r') as f:
            self.songToRdio = pickle.load(f)

        self.songMeta = {}
        with open(songMeta, 'r') as f:
            self.songMeta = pickle.load(f)
        pass

    def sample(self, before, after, not_list):
        not_list = json.decode(not_list)

        if before is None and after is None:
            return json.encode([])

        # TODO:   2011-09-20 12:59:44 by Brian McFee <bmcfee@cs.ucsd.edu>
        # this is where markov smarts goes             

        return json.encode([self.package('SOITXNB12A8C144ECD')])

    def package(self, song_id):
        S = {   'song_id': song_id, 
                'rdio_id': self.songToRdio[song_id],
                'artist':   self.songMeta[song_id]['artist'],
                'title':    self.songMeta[song_id]['title'] }
        return S

    def queue(self, qid):
        if qid in self.songToRdio and self.songToRdio[qid] is not None:
            return json.encode([self.package(qid)])
        else:
            return json.encode([self.package('SOCWJDB12A58A776AF')])
