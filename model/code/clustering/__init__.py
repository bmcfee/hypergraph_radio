#!/usr/bin/env python

import time
import numpy
import random


class FeatureMap(object):

    def __init__(self):
        self.__dimension = 0
        self.__data = {}
        pass

    def __setitem__(self, key, value):
        if len(self) == 0:
            self.__data[key] = value
            self.__dimension = len(value)
            return

        if len(value) != self.__dimension:
            raise ValueError('Dimension mismatch: dimension=%d, given d=%d' % (self.__dimension, len(value)))

        self.__data[key] = value

        pass

    def __getitem__(self, key):
        return self.__data[key]


    def __contains__(self, key):
        return key in self.__data


    def __len__(self):
        return len(self.__data)

    def __delitem__(self, key):
        del self.__data[key]
        pass

    def __iter__(self):
        return self.__data.__iter__()

    def iterkeys(self):
        return self.__data.iterkeys()

    def dimension(self):
        return self.__dimension



class Clustering(object):
    
    def __init__(self, points=None, description=None):
        self.__clusters     = []
        self.__description  = 'Clustering_' + str(time.time())

        if points is not None:
            if type(points) is not set:
                raise TypeError('points must be of type: set')
            self.__clusters.append(Cluster(None, points))

        if description is not None:
            if type(description) is not str:
                raise TypeError('description must be of type: str')
            self.__description = description
        pass


    def __iter__(self):
        for c in self.__clusters:
            yield c
        pass


    def __len__(self):
        return len(self.__clusters)

    
    def setDescription(self, desc):
        if type(desc) is not str:
            raise TypeError('description must be of type: str')

        self.__description = desc
        pass

    
    def getDescription(self):
        return self.__description

    
    def probability(self, x1, x2):
        for c in self:
            if x1 in c and x2 in c:
                return 1.0 / (len(c) - 1)
        return 0.0


    def adjoin(self, C2):
        for c in C2:
            self.add(c)
        pass


    def add(self, c):
        if type(c) is not Cluster:
            raise TypeError('attempting to add non-Cluster to Clustering')
        self.__clusters.append(c)
        pass


    def refine(self, k, X):
        R = None
        for c in self:
            if R is None:
                R = c.refine(k, X)
            else:
                R.adjoin(c.refine(k, X))
            pass
        return R

    def addpoint(self, x_id, x_vec):

        d = numpy.infty
        closest = 0
        for c in self:
            d_c = c.distance(x_vec)
            if d_c < d:
                d       = d_c
                closest = c
            pass

        closest.add(x_id)
        pass




class Cluster(object):

    def __init__(self, centroid=None, points=None):
        self.__points   = set()
        self.__centroid = None

        if centroid is not None:
            if type(centroid) is not numpy.ndarray:
                raise TypeError('centroid must be of type: numpy.ndarray')
            self.__centroid = centroid

        if points is not None:
            if type(points) is not set:
                raise TypeError('points must be of type: set')
            self.__points.update(points)

        pass

    def __contains__(self, x):
        return x in self.__points


    def __len__(self):
        return len(self.__points)


    def add(self, x):
        self.__points.add(x)
        pass


    def distance(self, v):
        return sum((self.__centroid - v)**2)


    def refine(self, k, X):
        
        # get the new centroids
        centers = onlineKmeans(k, self.__points, X)

        # construct a new clustering
        C = Clustering()
        for mu in centers:
            C.add(Cluster(mu))

        # add data to the clustering
        for x in self.__points:
            C.addpoint(x, X[x])

        return C

    def __iter__(self):
        return self.__points.__iter__()


def onlineKmeans(k, points, X, use_lloyd=False):


    def lloyd(mu,x,n):
        return sum((mu -x)**2)
        
    def hartigan(mu, x, n):
        return lloyd(mu, x, n) * n / (n + 1.0)

    # 1: randomly permute the point set
    points = list(points)
    random.shuffle(points)

    # 2. allocate cluster counters
    counters = numpy.zeros(k)

    # 3. allocate centroids
    centroids = numpy.zeros([k, X.dimension()])

    score = hartigan
    if use_lloyd:
        score = lloyd
        pass

    for (i, x) in enumerate(points):
        # Initialize centroids to the first k points
        if i < k:
            centroids[i,:]  = X[x].copy()
            counters[i]     = 1.0
            continue

        # Find the closest centroid
        distance    = numpy.infty
        closest     = 0
        for (j, mu) in enumerate(centroids):
            nd = score(mu, X[x], counters[j])
            if nd < distance:
                closest     = j
                distance    = nd
            pass

        # Update centroid
        centroids[closest,:] = (centroids[closest,:] * counters[closest] + X[x]) / (counters[closest] + 1.0)
        counters[closest] += 1.0

        pass

    return centroids
