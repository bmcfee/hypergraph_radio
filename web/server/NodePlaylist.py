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

    def index(self):
        return json.encode([self.package(X) for X in ['SOWWHEW12A81C21D9D']])

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
