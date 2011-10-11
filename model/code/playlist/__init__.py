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

        (gamma, xi, l) = self.forwardBackward(clusterings, model)
        return l


    def forwardBackward_unnormalized(self, clusterings, model):

        n = len(clusterings)
        T = len(self.__songs)

        # initialization
        alpha       = numpy.zeros((T,n))
        alpha[0,:]  = model['pi'] * [c.probability(self.__songs[0]) for c in clusterings]

        beta        = numpy.zeros((T,n))
        beta[T-1,:] = 1


        for t in range(1,T):
            # forward pass
            alpha[t,:] = [c.probability(self.__songs[t-1], self.__songs[t]) for c in clusterings]
            alpha[t,:] = alpha[t,:] * numpy.dot(alpha[t-1,:], model['A'])

            # backward pass
            beta[T-t,:] = [c.probability(self.__songs[T-t], self.__songs[T-t+1]) for c in clusterings]
            beta[T-t,:] = beta[T-t+1,:] * numpy.dot(beta[T-t,:], model['A'])
            pass

        l       = numpy.sum(alpha[T-1,:])       # likelihood of the observation
        gamma   = alpha * beta                  # state posteriors
        xi      = numpy.zeros((n,n))            # transition joint probabilities
        pass


    def forwardBackward(self, clusterings, model):
        n = len(clusterings)
        T = len(self.__songs)

        alpha_hat       = numpy.zeros((T,n))
        beta_hat        = numpy.zeros((T,n))
        c               = numpy.zeros(T)
        likelihood      = 1.0

        # initialization
        alpha_hat[0,:]  = model['pi'] * [c.probability(self.__songs[0]) for c in clusterings]
        c[0]            = numpy.sum(alpha_hat[0,:])
        likelihood     *= c[0]

        # forward pass
        for t in range(1,T):
            alpha_hat[t,:]  =   [c.probability(self.__songs[t-1], self.__songs[t]) for c in clusterings]
            alpha_hat[t,:]  =   alpha_hat[t,:] * numpy.dot(alpha_hat[t-1,:], model['A'])
            c[t]            =   numpy.sum(alpha_hat[t,:])
            alpha_hat[t,:]  /=  c[t]
            likelihood      *=  c[t]
            pass

        # backward pass
        beta_hat[-1,:]      = 1.0 
        for t in range(T-1):
            beta_hat[T-t,:]   = [c.probability(self.__songs[T-t], self.__songs[T-t+1]) for c in clusterings]
            beta_hat[T-t,:]   = beta_hat[T-t+1,:] * numpy.dot(beta[T-t,:], model['A']) / c[T-t+1]
            pass

        gamma   = alpha_hat * beta_hat
        xi      = numpy.zeros((n,n))

        for t in range(1,T):
            # c(t)^-1 * alpha(t-1) * p(xt | xt-1, zt) * p(zt | zt-1) * beta(t)

            # z_t dependent
            xi_new  =   beta_hat[t]
            xi_new  *=  [c.probability(self.__songs[t-1], self.__songs[t]) for c in clusterings]

            # z_t-1 dependent
            xi_new  =   numpy.outer(alpha_hat[t-1], xi_new)
            xi      += xi_new * model['A'] / c[t]
            pass
    
        return (gamma[0,:], xi, likelihood)
        pass
