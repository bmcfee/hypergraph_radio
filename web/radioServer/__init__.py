#!/usr/bin/env python

import sqlite3
import contextlib
import cjson as json

import flask

import ConfigParser

import rdio, search, playlist, en

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

def run(**kwargs):
    app.run(**kwargs)
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

    # set up the echonest bindings
    if not hasattr(flask.g, 'en'):
        flask.g.en  = en.en(app.config)
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
    return json.encode([playlist.getSongInfo(flask.request.args['query'])])

@app.route('/playlist', methods=['POST'])
def webPlaylist():
    '''
        Choose the next song, given a current song and a list of forbidden songs
    '''
    seeds       = json.decode(flask.request.form.get('seeds', ''))
    not_list    = json.decode(flask.request.form.get('not_list', ''))

    return json.encode(playlist.nextSong(seeds, not_list))

@app.route('/artistbio', methods=['GET'])
def webArtistBio():
    '''
        Get the biography for an artist
    '''
    song_id = flask.request.args['song_id']
    cur = flask.g.db.cursor()
    try:
        cur.execute('''SELECT artist_id FROM song WHERE song.id = ?''', (song_id,))
        artist_id = cur.fetchone()[0]
        bio = flask.g.en.bio(artist_id)
        
        biostr = flask.render_template('bio.html', biography=bio[0], attribution_url=bio[1], attribution=bio[2])
        
    except:
        biostr = ''

    return json.encode({'song_id': song_id, 'bio': biostr})

@app.route('/test')
def webTest():
    '''
        Just a dummy function to test out flask
    '''
    cur = flask.g.db.cursor()
    cur.execute('''SELECT * FROM Artist INNER JOIN Song ON Artist.id = Song.artist_id LIMIT 10''')
    return json.encode([x for x in cur])

