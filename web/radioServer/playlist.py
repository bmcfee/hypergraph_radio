import flask
import numpy, numpy.random

def nextSong(before, not_list):

    MODEL_ID = 1
    # Get a cursor
    cur = flask.g.db.cursor()

    # Get the edges and weights for the previous song
    cur.execute('''SELECT           song_to_edge.edge_id,
                                    model_to_edge.weight
                    FROM            song_to_edge 
                    INNER JOIN      model_to_edge
                            ON      model_to_edge.edge_id = song_to_edge.edge_id
                    WHERE           song_id = ?
                            AND     model_to_edge.model_id = ?''', (before, MODEL_ID))

    edges = []
    edgeWeights = {}
    for (edge_id, weight) in cur:
        edges.append(int(edge_id))
        edgeWeights[int(edge_id)] = weight
        pass


    # Choose an edge
    weights = numpy.zeros(len(edges))
    for (i, e) in enumerate(edges):
        if e in edgeWeights:
            weights[i] = edgeWeights[e]
            pass
        pass


    try:
        weights /= numpy.sum(weights)
    except:
        weights = numpy.ones_like(weights) / len(weights)
        pass
    nextEdge = edges[numpy.argmax(numpy.random.multinomial(1, weights))]

    cur.execute('''SELECT description FROM edge WHERE edge.id = ?''', (nextEdge,))
    edgeDesc = cur.fetchone()[0]

    # Choose a song
    NL = ','.join(not_list)
    cur.execute('''SELECT count(song_id) FROM song_to_edge WHERE edge_id = ? and song_id not in (?)''',
                (nextEdge, NL))
    
    numSongs    = cur.fetchone()[0]
    offset      = numpy.random.randint(0, numSongs, 1)[0]
    cur.execute('''SELECT song_id FROM song_to_edge WHERE edge_id = ? and song_id not in (?) 
                    LIMIT ?, 1''',
                (nextEdge, NL, int(offset)))

    nextSongId  = cur.fetchone()[0]

    # Get the song info

    info = getSongInfo(nextSongId)
    info['edge'] = edgeDesc
    return [info]


def getSongInfo(song_id):

    cur = flask.g.db.cursor()
    cur.execute('''SELECT       Song.id         as song_id, 
                                Song.rdio_id    as rdio_id, 
                                Song.title      as title, 
                                Artist.name     as artist
                    FROM        Song
                    INNER JOIN  Artist ON Song.artist_id = Artist.id
                    WHERE       Song.id = ?
                    LIMIT       1''', (song_id,))
    try:
        (song_id, rdio_id, title, artist) = cur.fetchone()
        return {   'song_id':  song_id, 
                                    'rdio_id':  rdio_id, 
                                    'title':    title, 
                                    'artist':   artist}
    except:
        pass

    return {}


