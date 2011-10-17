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


#---#


class Clustering(object):
    
    def __init__(self, points=None, description=None):
        self.__clusters     = []
        self.__description  = 'Clustering_' + str(time.time())

        if points is not None:
            self.__clusters.append(Cluster(points=points))
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

    def __getitem__(self, key):
        return self.__clusters[key]
    
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

            elif x2 != x1:
                for c in activeSets:
                    if x2 in c and len(c) > 1:
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

    def sample(self, x_id=None):
        if x_id is None:
            activeSets  = self.__clusters
            pass
        else:
            activeSets  = filter(lambda c: x_id in c, self)
            pass

        if len(activeSets) == 0:
            raise IndexError('%s not found in clustering' % x_id)

        return random.sample(activeSets, 1)[0].sample(x_id)
        pass

    def prune(self):
        self.__clusters = filter(lambda c: len(c) > 0, self.__clusters)
        pass

    def __repr__(self):
        return self[:].__repr__()

class SpillTree(Clustering):
    
    def __init__(self, points=None, description=None):
        super(SpillTree, self).__init__(None, description)

        if points is not None:
            self.__clusters.append(SpillNode(None, points))

        pass

    def adjoin(self, C2):

        if not isinstance(C2, SpillTree):
            raise TypeError('Trying to adjoin from non-SpillTree')

        for c in C2:
            self.add(c)

        pass

    def add(self, c):
        if not isinstance(c, SpillNode):
            raise TypeError('attempting to add non-SpillNode to SpillTree')
        self.__clusters.append(c)
        pass

    def refine(self, X):
        R = None
        print 'Refining SpillTree: [%s]%s' % (' ' * len(self), '\b' * (len(self)+1)),
        for c in self:
            if R is None:
                R = c.refine(X)
            else:
                R.adjoin(c.refine(X))
            print '\b#',
            pass
        print
        return R


#---#


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


    def __iter__(self):
        return self.__points.__iter__()

    def sample(self, x_id=None):
        if x_id is None:
            return random.sample(self.__points, 1)
        elif x_id in self:
            return random.sample(self.__points - set([x_id]), 1)
        
        raise IndexError('%s not found in cluster' % x_id)
        pass

    def __repr__(self):
        return 'Cluster(points=%s)' % (self.__points.__repr__())


    def distance(self, v, mu=None):
        if mu is None:
            mu = self.__centroid
        return sum((mu - v)**2)


    def refine(self, k, X):
        
        # get the new centroids
        clusters    = [Cluster(centroid=mu) for mu in self.onlineKmeans(k, self.__points, X)]

        # add data to the clustering
        for x_id in self.__points:
            if x_id in X:
                j = numpy.argmin([c.distance(X[x_id]) for c in clusters])
                clusters[j].add(x_id)
            pass

        # construct a new clustering
        C = Clustering()
        for c in clusters:
            C.add(c)
            pass

        C.prune()
        return C


    def onlineKmeans(self, k, points, X, minCount=5000):

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
                    nd = self.distance(mu, X[x]) * counters[j] / (counters[j] + 1.0)
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


# class SpillNode(Cluster):
    
