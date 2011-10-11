import numpy
import clustering

class Playlist(object):
    
    def __init__(self, songs):
        self.__songs = songs
        pass

    def likelihood(self, clusterings, model):
        # clusterings = list of m clusterings
        # model = hash {'pi': initial clustering distribution over m clusterings
        #               'A': m-by-m transition matrix

        (gamma, xi, ll) = self.forwardBackward(clusterings, model)
        return ll

    def forwardBackward(self, clusterings, model):
        n = len(clusterings)
        T = len(self.__songs)

        alpha_hat       = numpy.zeros((T,n))
        beta_hat        = numpy.zeros((T,n))
        c               = numpy.zeros(T)

        # initialization
        alpha_hat[0,:]  = model['pi'] * [C.probability(self.__songs[0]) for C in clusterings]
        c[0]            = numpy.sum(alpha_hat[0,:])
        ll              = numpy.log(c[0])

        # forward pass
        for t in range(1,T):
            alpha_hat[t,:]  =   [C.probability(self.__songs[t-1], self.__songs[t]) for C in clusterings]
            alpha_hat[t,:]  =   alpha_hat[t,:] * numpy.dot(alpha_hat[t-1,:], model['A'])
            c[t]            =   numpy.sum(alpha_hat[t,:])
            alpha_hat[t,:]  /=  c[t]
            ll              +=  numpy.log(c[t])
            pass


        # backward pass
        beta_hat[-1,:]      = 1.0 
        for t in range(T-2,-1,-1):
            beta_hat[t,:]   = [C.probability(self.__songs[t], self.__songs[t+1]) for C in clusterings]
            beta_hat[t,:]   = beta_hat[t+1,:] * numpy.dot(beta_hat[t,:], model['A']) / c[t+1]
            pass

        gamma   = alpha_hat * beta_hat
        xi      = numpy.zeros((n,n))

        for t in range(1,T):
            # c(t)^-1 * alpha(t-1) * p(xt | xt-1, zt) * p(zt | zt-1) * beta(t)

            # z_t dependent
            xi_new  =   beta_hat[t]
            xi_new  *=  [C.probability(self.__songs[t-1], self.__songs[t]) for C in clusterings]

            # z_t-1 dependent
            xi_new  =   numpy.outer(alpha_hat[t-1], xi_new)
            xi      += xi_new * model['A'] / c[t]
            pass
    
        return (gamma[0,:] / sum(gamma[0,:]), xi / sum(sum(xi)), ll)
        pass
