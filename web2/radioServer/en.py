import urllib2
import json
import pprint

class en(object):
    def __init__(self, cfg):
        self.api_key    = cfg['echonest_api_key']
        self.root       = 'http://developer.echonest.com/api/v4'
        self.biocache   = {}
        pass

    def bio(self, artist_id):
        
        if artist_id in self.biocache:
            return self.biocache[artist_id]

        url = '%s/artist/biographies?api_key=%s&id=%s&format=json' % (self.root, self.api_key, artist_id)
        try:
            f = urllib2.urlopen(url)
            S = json.loads(f.read())
            bio = S['response']['biographies'][0]
            for B in S['response']['biographies']:
                if (not hasattr(bio, 'truncated')) or (not bio['truncated']):
                    bio = B
                    break
                pass
            self.biocache[artist_id] = (bio['text'], bio['license']['attribution-url'], bio['license']['attribution'])
            return self.biocache[artist_id]
        except:
            pass
