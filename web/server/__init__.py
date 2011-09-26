import cherrypy
from cherrypy.lib.static import serve_file

from ConfigParser import SafeConfigParser
import os
import cjson as json

import NodeRdio, NodeSearch
import MyEchoNest


class Root:

    def __init__(self, serverIni):

        self.config     = SafeConfigParser()
        self.config.read(serverIni)

        self.basedir    = self.config.get('server', 'root')
        self.staticdir  = os.path.join(self.basedir, self.config.get('server', 'static'))

        self._rdio      = NodeRdio.Root(    self.config.get('rdio', 'api_key'), 
                                            self.config.get('rdio', 'secret'),
                                            self.config.get('rdio', 'domain'),
                                            self.config.get('rdio', 'playback_ttl'))

        self._search    = NodeSearch.Root(  
                                os.path.join(self.basedir, self.config.get('server', 'text_index')),
                                os.path.join(self.basedir, self.config.get('server', 'song_meta')),
                                os.path.join(self.basedir, self.config.get('server', 'rdio_index')),
                                os.path.join(self.basedir, self.config.get('server', 'playlist_model')))

        self._EN        = MyEchoNest.EN(self.config.get('echonest', 'api_key'))

        self._cp_config = { 'tools.staticdir.on': True,
                            'tools.staticdir.dir' : self.staticdir }
        pass

    @cherrypy.expose
    def rdio(self):
        self._rdio.refresh()
        return json.encode(self._rdio.index())
        pass

    @cherrypy.expose
    def playlist(self, before=None, after=None, not_list=None, tag_filter=None):
        self._rdio.refresh()
        return json.encode(self._search.sample(before, after, json.decode(not_list), json.decode(tag_filter)))
        pass
    
    @cherrypy.expose
    def queue(self, query=None):
        self._rdio.refresh()
        return json.encode(self._search.queue(query))

    @cherrypy.expose
    def search(self, query=None):
        self._rdio.refresh()
        return json.encode(self._search.search(query))

    @cherrypy.expose
    def terms(self):
        return json.encode(self._search.all_terms())

    @cherrypy.expose
    def tags(self, query=None):
        self._rdio.refresh()
        return json.encode(self._search.tags(query))

    @cherrypy.expose
    def artist(self, query=None):
        self._rdio.refresh()
        return json.encode(self._search.artist(self._EN, query))

    @cherrypy.expose
    def index(self):
        self._rdio.refresh()
        return serve_file(os.path.join(self.staticdir, 'player.html'), content_type='text/html')


