#!/usr/bin/env python

import time
import numpy, scipy.stats
import random

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
        self._clusters     = []
        self._description  = 'Clustering_' + str(time.time())

        if points is not None:
            self._clusters.append(Cluster(points=points))
            pass

        if description is not None:
            self.setDescription(description)
            pass
        pass


    def __iter__(self):
        for c in self._clusters:
            yield c
        pass


    def __len__(self):
        return len(self._clusters)

    def __getitem__(self, key):
        return self._clusters[key]
    
    def setDescription(self, desc):
        if not isinstance(desc, str):
            raise TypeError('description must be of type: str')

        self._description = desc
        pass

    
    def getDescription(self):
        return self._description

    
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
            raise TypeError('Attempting to adjoin from non-Clustering')

        for c in C2:
            self.add(c)

        pass


    def add(self, c):
        if not isinstance(c, Cluster):
            raise TypeError('Attempting to add non-Cluster to Clustering')
        self._clusters.append(c)
        pass


    def refine(self, **kwargs):
        R = None
        print 'Refining sets: [%s]%s' % (' ' * len(self), '\b' * (len(self)+1)),
        for c in self:
            if R is None:
                R = c.refine(**kwargs)
            else:
                R.adjoin(c.refine(**kwargs))
            print '\b#',
            pass
        print 
        return R

    def sample(self, x_id=None):
        if x_id is None:
            activeSets  = self._clusters
            pass
        else:
            activeSets  = filter(lambda c: x_id in c and len(c) > 1, self)
            pass

        if len(activeSets) == 0:
            raise IndexError('%s not found in clustering' % x_id)

        return random.sample(activeSets, 1)[0].sample(x_id)
        pass

    def prune(self):
        self._clusters = filter(lambda c: len(c) > 0, self._clusters)
        pass

    def __repr__(self):
        return self[:].__repr__()



class SpillTree(Clustering):
    
    def __init__(self, points=None, description=None):
        super(SpillTree, self).__init__(None, description)

        if points is not None:
            self._clusters.append(SpillNode(None, points))

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
        self._clusters.append(c)
        pass

#---#


class Cluster(object):

    def __init__(self, centroid=None, points=None):

        if centroid is not None and not isinstance(centroid, numpy.ndarray):
            raise TypeError('centroid must be of type: numpy.ndarray')

        self.__centroid = centroid

        if points is not None:
            self._points   = set(points)
        else:
            self._points   = set()

        pass


    def __contains__(self, x):
        return x in self._points


    def __len__(self):
        return len(self._points)


    def add(self, x):
        self._points.add(x)
        pass


    def __iter__(self):
        return self._points.__iter__()

    def sample(self, x_id=None):
        if x_id is None:
            return random.sample(self._points, 1)[0]
        elif x_id in self:
            return random.sample(self._points - set([x_id]), 1)[0]
        
        raise IndexError('key %s not found' % x_id)
        pass

    def __repr__(self):
        return 'Cluster(points=%s)' % (self._points.__repr__())



    def refine(self, **kwargs):
        
        X           = kwargs.get('X')
        k           = kwargs.get('k', 2)
        minCount    = kwargs.get('minCount', 5000)

        def D(u, v):
            return sum((u - v)**2)

        def onlineKmeans(points):

            # 1. allocate cluster counters
            counters    = numpy.zeros(k)

            # 2. allocate centroids
            centroids   = numpy.zeros([k, X.dimension()])

            if len(points) == 0:
                return centroids

            for count in range(0, minCount, len(points)):
                random.shuffle(points)
                for x in points:
                    # Find the closest centroid
                    # Hartigan initializes centroids to the first k distinct points 
                    j_min = numpy.argmin([D(X[x], mu) * c / (c+1.0) for (mu, c) in zip(centroids, counters)]) 

                    # Update centroid
                    centroids[j_min,:] = (centroids[j_min,:] * counters[j_min] + X[x]) / (counters[j_min] + 1.0)
                    counters[j_min]   += 1.0

                    pass
                pass
    
            return centroids


        # get the new centroids
        #   only retain points with feature representation
        points      = filter(lambda p: p in X, self._points)
        centroids   = onlineKmeans(points)
        clusters    = [Cluster(centroid=mu) for mu in centroids]

        # add data to the clustering
        for x_id in points:
            j = numpy.argmin([D(X[x_id], mu) for (c, mu) in zip(clusters, centroids)])
            clusters[j].add(x_id)
            pass

        # construct a new clustering
        C = Clustering()
        for c in clusters:
            C.add(c)
            pass

        C.prune()
        return C



class SpillNode(Cluster):
    
    def refine(self, **kwargs):
        X   = kwargs.get('X')
        tau = kwargs.get('tau', 0.1)

        def topPCA(points):
            d           = X.dimension()
            m1          = numpy.zeros(d)
            m2          = numpy.zeros([d, d])
            n           = 1.0 * len(points)

            for x_id in points:
                m1      +=  X[x_id]
                m2      +=  numpy.outer(X[x_id], X[x_id].T)

            m1          /=  n
            sigma       =   (m2 - ( n * numpy.outer(m1, m1.T) ) ) / (n - 1.0)
            
            (l,v)   =   numpy.linalg.eigh(sigma)
            w           =   v[:,numpy.argmax(l)]
            return w
            
        def splitPCA(points):
            # 1. compute PCA direction
            w               =   topPCA(points)

            # 2. compute bias points
            wx = {}
            for x_id in points:
                wx[x_id]    =   numpy.dot(w, X[x_id])

            b               =   scipy.stats.mstats.mquantiles(wx.values(), [0.5 - tau, 0.5 + tau])
            
            # 3. partition the set
            left_set    = set()
            right_set   = set()

            for (x_id, score) in wx.iteritems():
                if score <= b[-1]:
                    left_set.add(x_id)
                if score >  b[0]:
                    right_set.add(x_id)
                pass
            
            return (left_set, right_set)

        points          = filter(lambda p: p in X, self._points)

        (L, R)          = splitPCA(points)

        C               = SpillTree()
        C.add(SpillNode(points=L))
        C.add(SpillNode(points=R))
        C.prune()

        return C

    def __repr__(self):
        return 'SpillNode(points=%s)' % (self._points.__repr__())

