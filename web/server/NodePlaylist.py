import cjson as json
import cPickle as pickle

class Root(object):
    def __init__(self, rdioMap):
        self.songToRdio = {}
        with open(rdioMap, 'r') as f:
            self.songToRdio = pickle.load(f)
        pass

    def index(self):
        return json.encode(['t2895734', 't3150820', 't1281681'])

    def queue(self, qid):
        if qid in self.songToRdio and self.songToRdio[qid] is not None:
            return json.encode([self.songToRdio[qid]])
        else:
            return json.encode(["t2897022"])
