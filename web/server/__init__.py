import cherrypy
from cherrypy.lib.static import serve_file

from ConfigParser import SafeConfigParser
import os

import NodeRdio
import NodePlaylist
import NodeSearch



class Root:


    def __init__(self, serverIni):

        self.config     = SafeConfigParser()
        self.config.read(serverIni)

        self.basedir    = self.config.get('server', 'root')
        self.staticdir  = os.path.join(self.basedir, self.config.get('server', 'static'))


        self._playlist  = NodePlaylist.Root()
        self._rdio      = NodeRdio.Root(    self.config.get('rdio', 'api_key'), 
                                            self.config.get('rdio', 'secret'),
                                            self.config.get('rdio', 'domain'))
        self._search    = NodeSearch.Root(  os.path.join(self.basedir, self.config.get('server', 'text_index')))

        self._cp_config = { 'tools.staticdir.on': True,
                            'tools.staticdir.dir' : self.staticdir }
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
    def search(self, query=None):
        return self._search.search(query)

    @cherrypy.expose
    def index(self):
        return serve_file(os.path.join(self.staticdir, 'player.html'), content_type='text/html')
        pass

