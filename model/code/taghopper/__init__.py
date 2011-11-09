#!/usr/bin/env python

import random
import numpy

def sampleFromMultinomial(p):
    for (i,v) in enumerate(numpy.random.multinomial(1, p)):
        if v > 0:
            return i
    pass

class TagVector(set):
    def __init__(self, a):
        super(TagVector, self).__init__(a)
        pass

    def __repr__(self):
        return super(TagVector, self).__repr__()

    def __str__(self):
        return super(TagVector, self).__str__()

    def __and__(self, b):
        if isinstance(b, TagVector):
            return TagVector(set(self) & set(b))
        elif isinstance(b, numpy.ndarray):
            c = numpy.zeros(b.shape)
            for i in self:
                c[i] = b[i]
            return c
        raise TypeError("Argument type not supported: %s" % type(b))
        pass

    def __mul__(self, b):
        return self.__and__(b)
        pass

#---#

class FeatureMap(dict):
    def __init__(self, vocab):
        self.__vocabulary   = vocab
        self.__vocabIndex   = {}
        for (i,v) in enumerate(self.__vocabulary):
            self.__vocabIndex[v] = i
            pass
        pass

    def __setitem__(self, key, value):
        idx = [self.__vocabIndex[v] for v in value]
        super(FeatureMap, self).__setitem__(key, TagVector(idx))
        pass

    def clear(self):
        del self.__vocabulary
        super(FeatureMap, self).clear()
        pass

    def getVocab(self):
        return self.__vocabulary

    def getVocabIndex(self):
        return self.__vocabIndex

    def tagnum(self, k):
        return self.__vocabulary[k]

    def tagItem(self, x):
        return [self.__vocabulary[i] for i in x]

    def dimension(self):
        return len(self.__vocabulary)

    def condense(self):

        MIN_USAGE = 10
        # Find all the used tags
        n = self.dimension()

        used = [0] * n
        for (k, x) in self.iteritems():
            for tag in x:
                used[tag] += 1

        # Build a new featuremap with condensed representation
        newvocab = []
        for i in xrange(n):
            if used[i] > MIN_USAGE:
                newvocab.append(self.__vocabulary[i])
            pass

        F = FeatureMap(newvocab)
        
        # Populate new featuremap 
        vi = F.getVocabIndex()
        for (k, x) in self.iteritems():
            F[k] = filter(lambda t: t in vi, self.tagItem(x))
            pass
        return F
#---#

class Model(object):

    # This is where model parameters go:
    #   featuremap
    #   size of each tag set
    #   weighting over tags

    # methods:
    #   likelihood of a single point:   P(x)
    #   likelihood of a transition:     P(x2 | x1)
    #   transition vectors: ( (x1 * x2 * nu * rho), (x1 * nu) )
    def __init__(self, X, mu=None):
        self.X          = X
        self.__numtags  = X.dimension()
        if mu is None:
            self.mu     = numpy.ones(self.__numtags) / (1.0 * self.__numtags)
        else:
            self.mu     = mu
            pass
        
        self.counts     = numpy.zeros(self.__numtags)
        self.__tagsets  = [set() for i in range(len(self.counts))]

        for x in self.X:
            for v in X[x]:
                self.counts[v] += 1
                self.__tagsets[v].add(x)
                pass
            pass

        for v in range(self.__numtags):
            if self.counts[v] <= 1:
                self.mu[v] = 0
            pass
        self.mu /= numpy.sum(self.mu)

        self.__nu       = numpy.zeros(self.__numtags)
        self.__rho      = numpy.zeros(self.__numtags)
        for i in range(self.__numtags):
            if self.counts[i] > 0:
                self.__nu[i] = 1.0 / self.counts[i]
                if self.counts[i] > 1:
                    self.__rho[i] = 1.0 / (self.counts[i] - 1)
                    pass
                pass
            pass
        pass

    def transitionVectors(self, x1, x2):
        x1nu = self.X[x1] * self.__nu
        return ( self.X[x2] * self.__rho * x1nu, x1nu)

    def loglikelihood(self, x1, x2=None):
        if x2 is None:
            return numpy.log(numpy.dot(self.mu, self.X[x1] * self.__nu))
        else:
            (v1, v2) = self.transitionVectors(x1, x2)
            return numpy.log(numpy.dot(self.mu, v1)) - numpy.log(numpy.dot(self.mu, v2))
        pass

    def gradient(self, P):
        m       = len(P)

        v2      = self.X[P[0]] * self.__nu
        dx      = v2 / numpy.dot(self.mu, v2)

        for i in range(0, m-1):
            (v1, v2) = self.transitionVectors(P[i], P[i+1])
            dx      += v1 / numpy.dot(self.mu, v1) 
            dx      -= v2 / numpy.dot(self.mu, v2)
            pass

        return dx / m

    def playlistlikelihood(self, P):
        m   = len(P)
        ll  = self.loglikelihood(P[0])
        for i in range(0, m-1):
            ll += self.loglikelihood(P[i], P[i+1])
            pass
        return ll / m


    def sample(self, m):
        # Pick an initial tag
        tags    = [sampleFromMultinomial(self.mu)]
        songs   = random.sample(self.__tagsets[tags[-1]], 1)
        for i in range(m):
            mu  = self.X[songs[-1]] * self.mu
            mu /= numpy.sum(mu)
            tags.append(sampleFromMultinomial(mu))
            songs.extend(random.sample(self.__tagsets[tags[-1]] - set([songs[-1]]), 1))
        return (songs, tags)

#---#

