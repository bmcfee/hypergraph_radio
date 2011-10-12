import numpy
import clustering
import pprint

class Playlist(object):
    
    def __init__(self, songs):
        self.__songs = songs
        pass

    def __len__(self):
        return len(self.__songs)


    def likelihood(self, model):
        # clusterings = list of m clusterings
        # model = hash {'pi': initial clustering distribution over m clusterings
        #               'A': m-by-m transition matrix

        (gamma, xi, ll) = self.forwardBackward(model)
        return ll


    def forwardBackward(self, model):
        n = len(model['C'])
        T = len(self.__songs)

        alpha_hat       = numpy.zeros((T,n))
        beta_hat        = numpy.zeros((T,n))
        c               = numpy.zeros(T)

        # initialization
        alpha_hat[0,:]  = model['pi'] * [C.probability(self.__songs[0]) for C in model['C']]
        c[0]            = numpy.sum(alpha_hat[0,:])
        ll              = numpy.log(c[0])

        # forward pass
        for t in range(1,T):
            alpha_hat[t,:]  =   [C.probability(self.__songs[t-1], self.__songs[t]) for C in model['C']]
            alpha_hat[t,:]  =   alpha_hat[t,:] * numpy.dot(alpha_hat[t-1,:], model['A'])
            c[t]            =   numpy.sum(alpha_hat[t,:])
            alpha_hat[t,:]  /=  c[t]
            ll              +=  numpy.log(c[t])

            pass


        # backward pass
        beta_hat[-1,:]      = 1.0 
        for t in range(T-2,-1,-1):
            beta_hat[t,:]   = [C.probability(self.__songs[t], self.__songs[t+1]) for C in model['C']]
            beta_hat[t,:]   = beta_hat[t+1,:] * numpy.dot(model['A'], beta_hat[t,:]) / c[t+1]

            pass


        gamma   = alpha_hat * beta_hat
        xi      = numpy.zeros((n,n))

        for t in range(1,T):
            xi_new  =   beta_hat[t] * [C.probability(self.__songs[t-1], self.__songs[t]) for C in model['C']]
            xi_new  =   numpy.outer(alpha_hat[t-1], xi_new) * model['A'] / c[t]

            xi      += xi_new / sum(sum(xi_new))
            pass
    
        return (gamma[0,:] / sum(gamma[0,:]), xi, ll)
        pass
