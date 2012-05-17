#!/usr/bin/env python

import sqlite3
import contextlib
import cjson as json

import flask

import ConfigParser

import rdio, search

# build the app
app = flask.Flask(__name__)


def loadConfig(serverIni):
    P               = ConfigParser.RawConfigParser()
    P.optionxform   = str
    P.read(serverIni)

    CFG = {}
    for section in P.sections():
        CFG[section] = dict(P.items(section))
        pass

    for (k,v) in CFG['server'].iteritems():
        app.config[k] = v
        pass
    pass

def run():
    app.debug = app.config['Debug']
    app.run()
    pass


# --- server functions --- #

@app.before_request
def before_request():
    flask.g.db = sqlite3.connect(app.config['database'])

    # refresh the rdio key
    try: 
        flask.g.rdio.refresh()
    except:
        flask.g.rdio = rdio.rdio(app.config)
        pass

    # set up the searcher
    if not hasattr(flask.g, 'search'):
        flask.g.search = search.Search(app.config)
        pass

    pass

@app.teardown_request
def teardown_request(exception):
    if hasattr(flask.g, 'db'):
        flask.g.db.close()
        pass
    pass

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/rdio')
def getRdioToken():
    return json.encode(flask.g.rdio.getToken())

@app.route('/search', methods=['GET'])
def searchDB():
    return json.encode(flask.g.search.search(flask.request.args['q']))

@app.route('/test')
def index_test():
    cur = flask.g.db.cursor()
    cur.execute('''SELECT * FROM Artist INNER JOIN Song ON Artist.id = Song.artist_id LIMIT 10''')
    return json.encode([x for x in cur])

