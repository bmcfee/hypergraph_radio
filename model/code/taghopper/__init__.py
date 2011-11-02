#!/usr/bin/env python

import numpy

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
        super(FeatureMap, self).__setitem__(key, TagVector(v))
        pass

    def clear(self):
        del self.__vocabulary
        super(FeatureMap, self).clear()
        pass

    def getVocab(self):
        return self.__vocabulary

    def tagItem(self, x):
        return [self.__vocabulary[i] for i in x]

    def dimension(self):
        return len(self.__vocabulary)

#---#
