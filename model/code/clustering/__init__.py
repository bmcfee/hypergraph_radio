#!/usr/bin/env python

import time
import numpy
import random
import pprint

class FeatureMap(dict):

    def __init__(self, **kwargs):
        self.__dimension = None
        for (k,v) in kwargs.iteritems():
            if self.__dimension is None:
                self.__dimension = len(v)
            elif len(v) != self.__dimension:
                raise ValueError('Inconsistent dimensions in input data.')

        super(FeatureMap, self).__init__(kwargs)
        pass

    def __setitem__(self, key, value):
        if self.__dimension is None:
            self.__dimension = len(value)

        elif len(value) != self.__dimension:
            raise ValueError('Dimension mismatch: dimension=%d, given d=%d' % (self.__dimension, len(value)))

        super(FeatureMap, self).__setitem__(key, value)

        pass

    def clear(self):
        self.__dimension = None
        super(FeatureMap, self).clear()
        pass

    def dimension(self):
        return self.__dimension



class Clustering(object):
    
    def __init__(self, points=None, description=None):
        self.__clusters     = []
        self.__description  = 'Clustering_' + str(time.time())

        if points is not None:
            self.__clusters.append(Cluster(None, points))
            pass

        if description is not None:
            self.setDescription(description)
            pass
        pass


    def __iter__(self):
        for c in self.__clusters:
            yield c
        pass


    def __len__(self):
        return len(self.__clusters)

    
    def setDescription(self, desc):
        if not isinstance(desc, str):
            raise TypeError('description must be of type: str')

        self.__description = desc
        pass

    
    def getDescription(self):
        return self.__description

    
    def probability(self, x1, x2=None):

        activeSets  = filter(lambda c: x1 in c, self)
        nSets       = len(activeSets)

        P           = 0.0

        if nSets > 0:
            if x2 is None:
                for c in activeSets:
                    # Probability of choosing this set * probability choosing x1
                    P += 1.0 / (len(self) * len(c)) 
                    pass

            else:
                for c in activeSets:
                    if x2 in c:
                        # Probability of choosing this set * probability choosing x2
                        P += 1.0 / (nSets * (len(c) - 1))
                    pass
            pass
        return P


    def adjoin(self, C2):
        if not isinstance(C2, Clustering):
            raise TypeError('Trying to adjoin from non-clustering')

        for c in C2:
            self.add(c)

        pass


    def add(self, c):
        if not isinstance(c, Cluster):
            raise TypeError('attempting to add non-Cluster to Clustering')
        self.__clusters.append(c)
        pass


    def refine(self, k, X):
        R = None
        print 'Refining clusters: [%s]%s' % (' ' * len(self), '\b' * (len(self)+1)),
        for c in self:
            if R is None:
                R = c.refine(k, X)
            else:
                R.adjoin(c.refine(k, X))
            print '\b#',
            pass
        print 
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

    def sample(self, x_id=None):
        if x_id is None:
            activeSets  = self.__clusters
            pass
        else:
            activeSets  = filter(lambda c: x_id in c, self)
            pass

        if len(activeSets) == 0:
            raise IndexError('%s not found in clustering' % x_id)

        return random.sample(activeSets, 1).sample(x_id)
        pass

    def prune(self):
        self.__clusters = filter(lambda c: len(c) > 0, self.__clusters)
        pass



class Cluster(object):

    def __init__(self, centroid=None, points=None):
        self.__centroid = None

        if centroid is not None:
            if not isinstance(centroid, numpy.ndarray):
                raise TypeError('centroid must be of type: numpy.ndarray')
            self.__centroid = centroid
            pass

        if points is not None:
            self.__points = set(points)
        else:
            self.__points   = set()

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
            if x in X:
                C.addpoint(x, X[x])

        C.prune()
        return C

    def __iter__(self):
        return self.__points.__iter__()

    def sample(self, x_id=None):
        if x_id is None:
            return random.sample(self.__points, 1)
        elif x_id in self:
            return random.sample(self.__points - set([x_id]), 1)
        
        raise IndexError('%s not found in cluster' % x_id)
        pass



def onlineKmeans(k, points, X, minCount=5000):

    def score(mu, x, n):
        return sum((mu -x)**2) * n / (n + 1.0)

    # 1: randomly permute the point set
    #   only retain points with feature representation
    points = filter(lambda p: p in X, points)

    # 2. allocate cluster counters
    counters = numpy.zeros(k)

    # 3. allocate centroids
    centroids = numpy.zeros([k, X.dimension()])

    if len(points) == 0:
        return centroids

    count = 0
    while count < minCount:
        random.shuffle(points)
        for (i, x) in enumerate(points):
            # Find the closest centroid
            # This will initialize centroids to the first k points 
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
            count += 1

            pass
        pass

    return centroids
