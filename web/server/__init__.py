import cherrypy
from cherrypy.lib.static import serve_file

import rdioTalker
import playlist

from ConfigParser import SafeConfigParser

import pprint


class Root:


    def __init__(self, serverIni):

        self.config     = SafeConfigParser()
        self.config.read(serverIni)

        self._playlist  = playlist.Root()

        self._rdio      = rdioTalker.Root(  self.config.get('rdio', 'api_key'), 
                                            self.config.get('rdio', 'secret'),
                                            self.config.get('rdio', 'domain'))
        
        self._cp_config = { 'tools.staticdir.on': True,
                            'tools.staticdir.dir' : self.config.get('server', 'root') }
        pass

    @cherrypy.expose
    def rdio(self):
        return self._rdio.index()
        pass

    @cherrypy.expose
    def playlist(self):
        return self._playlist.index()
        pass

    @cherrypy.expose
    def index(self):
        return serve_file(self.config.get('server', 'root') + '/player.html', content_type='text/html')
        pass

