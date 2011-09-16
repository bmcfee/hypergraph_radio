import cherrypy
import cjson as json

class Root(object):
    @cherrypy.expose
    def index(self):
        return json.encode(['t2895734', 't3150820', 't1281681'])

        
