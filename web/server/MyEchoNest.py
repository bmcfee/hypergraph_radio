import urllib2
import cjson as json
import pprint

class EN(object):

    def __init__(self, api_key):
        self.api_key    = api_key
        self.root       = 'http://developer.echonest.com/api/v4'
        self._images    = {}
        self._bio       = {}
        pass

    def images(self, artist_id):
        
        if artist_id in self._images:
            return self._images[artist_id]

        url = '%s/artist/images?api_key=%s&id=%s&format=json' % (self.root, self.api_key, artist_id)

        f = urllib2.urlopen(url)
        S = json.decode(f.read())
        if 'response' in S and 'images' in S['response'] and len(S['response']['images']) > 0:
            self._images[artist_id] = S['response']['images'][0]['url']
            return self._images[artist_id]
        pass

    def bio(self, artist_id):

        if artist_id in self._bio:
            return self._bio[artist_id]

        url = '%s/artist/biographies?api_key=%s&id=%s&format=json' % (self.root, self.api_key, artist_id)
        f = urllib2.urlopen(url)
        S = json.decode(f.read())
        if 'response' in S and 'biographies' in S['response'] and len(S['response']['biographies']) > 0:
            self._bio[artist_id] = S['response']['biographies'][0]['text']
            return self._bio[artist_id]
        pass
