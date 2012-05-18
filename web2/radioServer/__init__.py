#!/usr/bin/env python

import sqlite3
import contextlib
import cjson as json

import flask

import ConfigParser

import rdio, search, playlist

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
    app.debug = True
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
def webIndex():
    '''
        Get the index page
    '''
    return flask.render_template('index.html')

@app.route('/rdio')
def webRdioToken():
    '''
        Get the Rdio token
    '''
    return json.encode(flask.g.rdio.getToken())

@app.route('/search', methods=['GET'])
def webSearch():
    '''
        Interface to the full-text search
    '''
    return json.encode(flask.g.search.search(flask.request.args['q']))

@app.route('/song', methods=['GET'])
def webSong():
    '''
        Given a song id, return the title, artist, and rdio_id
    '''
    cur = flask.g.db.cursor()
    cur.execute('''SELECT       Song.id         as song_id, 
                                Song.rdio_id    as rdio_id, 
                                Song.title      as title, 
                                Artist.name     as artist
                    FROM        Song
                    INNER JOIN  Artist ON Song.artist_id = Artist.id
                    WHERE       Song.id = ?
                    LIMIT       1''', (flask.request.args['query'],))
    try:
        (song_id, rdio_id, title, artist) = cur.fetchone()
        return json.encode( [   {   'song_id':  song_id, 
                                    'rdio_id':  rdio_id, 
                                    'title':    title, 
                                    'artist':   artist}])
    except:
        return json.encode([])
    pass

@app.route('/playlist', methods=['POST'])
def webPlaylist():
    '''
        Choose the next song, given a current song and a list of forbidden songs
    '''
    before      = flask.request.form.get('before', '')
    not_list    = json.decode(flask.request.form.get('not_list', ''))

    return json.encode(playlist.nextSong(before, not_list))

@app.route('/test')
def webTest():
    '''
        Just a dummy function to test out flask
    '''
    cur = flask.g.db.cursor()
    cur.execute('''SELECT * FROM Artist INNER JOIN Song ON Artist.id = Song.artist_id LIMIT 10''')
    return json.encode([x for x in cur])

