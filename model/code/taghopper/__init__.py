#!/usr/bin/env python

import numpy

class tagVector(set):
    def __init__(self, a):
        self.__index = set()
        if isinstance(a, set):
            self.__index.update(a)
        else:
            raise TypeError("Input object must be of type: set")
        pass

    def getTags(self):
        return self.__index

    def __len__(self):
        return len(self.__index)

    def __contains__(self, val):
        return val in self.__index

    def __iter__(self):
        return self.__index.__iter__()

    def __repr__(self):
        return 'tagVector(%s)' % self.__index.__repr__()

    def __str__(self):
        return 'tagVector(%s)' % self.__index.__str__()

    def __and__(self, b):
        if isinstance(b, tagVector):
            return tagVector(self.__index & b.getTags())
        elif isinstance(b, numpy.ndarray):
            c = numpy.zeros(b.shape)
            for i in self.__index:
                c[i] = b[i]
            return c
        raise TypeError("Argument type not supported: %s" % type(b))
        pass

    def __mul__(self, b):
        return self.__and__(b)
        pass


