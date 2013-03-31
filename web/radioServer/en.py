""" Wrapper class for echo nest API """

import urllib2
import json

class en(object):
    def __init__(self, cfg):
        """Build an echo nest wrapper object
        Arguments:
            cfg --  (dict)  from configparser

        cfg['echonest_api_key'] should contain the private key
        """
        self.api_key    = cfg['echonest_api_key']
        self.root       = 'http://developer.echonest.com/api/v4'
        self.biocache   = {}


    def bio(self, artist_id):
        
        if artist_id in self.biocache:
            return self.biocache[artist_id]

        url = '%s/artist/biographies?api_key=%s&id=%s&format=json' % (
                    self.root, self.api_key, artist_id)
        try:
            f = urllib2.urlopen(url)
            S = json.loads(f.read())
            bio = S['response']['biographies'][0]
            for B in S['response']['biographies']:
                if (not hasattr(bio, 'truncated')) or (not bio['truncated']):
                    bio = B
                    break
            self.biocache[artist_id] = (bio['text'], 
                                        bio['license']['attribution-url'], 
                                        bio['license']['attribution'])
            return self.biocache[artist_id]

        # FIXME:  2013-03-31 11:54:00 by Brian McFee <brm2132@columbia.edu>
        # bare exception
        except:
            pass

