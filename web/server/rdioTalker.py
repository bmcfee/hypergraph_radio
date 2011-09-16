import cherrypy
import rdio
import ConfigParser
import cjson as json

class Root(object):

    def __init__(self, rdioConfig):
        # Load the rdio config
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(rdioConfig)
        self.state = {}

        # initialize rdio object
        self.r = rdio.Rdio(self.config.get('rdio', 'api_key'), self.config.get('rdio', 'secret'), self.state)

        # get a playback token
        self.token = self.r.call('getPlaybackToken')
        pass

    @cherrypy.expose
    def index(self):
#         return json.encode({'playbackToken': self.token})
        return json.encode({'playbackToken': "GAlNi78J_____zlyYWs5ZG02N2pkaHlhcWsyOWJtYjkyN2xvY2FsaG9zdEbwl7EHvbylWSWFWYMZwfc="})
        pass

