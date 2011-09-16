import cherrypy
import rdioTalker
import playlist

import pprint

class Root(object):
    @cherrypy.expose
    def index(self):
        return "Hello World!"


# cherrypy.config.update({'log.screen': True})
pprint.pprint(cherrypy.config)
# conf = {'/': {      'tools.staticdir.on': True,
#                     'tools.staticdir.dir': '/home/bmcfee/git/radio/web/static',
#                     'tools.staticdir.content_types': {  'html': 'text/html',
#                                                         'swf': 'application/x-shockwave-flash',
#                                                         'js': 'text/javascript'}}}
root            = Root()
root.rdio       = rdioTalker.Root('rdio.ini')
root.playlist   = playlist.Root()
# app             = cherrypy.tree.mount(root, script_name='/', config=conf)
app             = cherrypy.tree.mount(root, script_name='/')

cherrypy.server.start()

