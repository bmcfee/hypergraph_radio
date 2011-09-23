import rdioapi
import time

class Root(object):

    def __init__(self, api_key, secret, domain, ttl):
        self.api_key    = api_key
        self.secret     = secret
        self.domain     = domain
        self.ttl        = ttl

        self.state = {}

        # initialize rdio object
        self.r = rdioapi.Rdio(api_key, secret, self.state)

        # get a playback token
        self.token = self.r.call('getPlaybackToken', domain=domain)
        self.timestamp = time.time()
        pass

    def refresh(self):
        if time.time() - self.timestamp > self.ttl:
            self.__init__(self.api_key, self.secret, self.domain, self.ttl)

    def index(self):
        return {'playbackToken': self.token, 'domain': self.domain}
        pass

