#!/usr/bin/env python

import cPickle as pickle
import sqlite3
import sys
import pprint

def loadModels(infile):

    with open(infile, 'r') as f:
        weights = pickle.load(f)
        pass

#     W = {}
#     for k in P['weights']:
#         W[k] = P['weights'][k][0]
#         pass
    return {'Genre': weights['w']}


def importWeights(dbc, weights):

    # 1. get edge mapping
    edgeMap = {}
    cur = dbc.cursor()

    cur.execute('''SELECT id, description FROM edge''')

    for (edge_id, edge_name) in cur:
        edgeMap[edge_name] = edge_id
        pass

    def edgeGenerator(m_id, eMap, W):
        for edgeName in eMap:
            if edgeName in W:
                yield (m_id, eMap[edgeName], W[edgeName])
        pass

    for n in weights:
        print 'Importing ', n
        # 1. install the model
        cur.execute('''INSERT INTO model (name) VALUES (?)''', (n,))
        # 2. get the new model's id
        model_id = cur.lastrowid

        cur.executemany('''INSERT INTO model_to_edge (model_id, edge_id, weight)
                                VALUES (?,?,?)''', 
                                edgeGenerator(model_id, edgeMap, weights[n]))
        pass


    dbc.commit()
    pass

if __name__ == '__main__':
    dbfile      = sys.argv[1]
    modelfile   = sys.argv[2]

    with sqlite3.connect(dbfile) as dbc:
        importWeights(dbc, loadModels(modelfile))
        pass
    pass
