import rdioapi
import cjson as json

class Root(object):

    def __init__(self, api_key, secret, domain):
        self.state = {}

        # initialize rdio object
        self.r = rdioapi.Rdio(api_key, secret, self.state)

        # get a playback token
        self.token = self.r.call('getPlaybackToken', domain=domain)
        pass

    def index(self):
        return json.encode({'playbackToken': self.token})
        pass

