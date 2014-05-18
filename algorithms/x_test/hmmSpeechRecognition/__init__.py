from math import log
import numpy
from numpy.lib.twodim_base import diag
from numpy.matlib import rand, repmat
from numpy.oldnumeric.mlab import cov
from numpy.oldnumeric.random_array import multivariate_normal

__author__ = 'Olexandr'


class Word:
    def __init__(self, name):
        self.name = str(name)
        #number of states
        self.n = 3
        #NxN transition probability matrix
        self.a = []
        #Nx1 initial state distribution vector
        self.prior = []
        #DxN mean vector (D = number of features)
        self.mu = []
        #DxDxN covariance matrix
        self.sigma = []

    def state_likelihood(self, observations):
        """
        Evaluates the Gaussian pdfs for each state at the observations
        Returns a matrix containing B(s, t) = f(O_t | S_t = s)
        """
        b = numpy.zeros(self.n, self.size(observations))

        for s in range(self.n):
            b[s, :] = multivariate_normal(numpy.transpose(observations), numpy.transpose(self.mu[:, s]), numpy.transpose(self.sigma[:, :, s]))
        return b

    def log_likelihood(self, observations):
        return self.forward(self, self.state_likelihood(observations))

    @staticmethod
    def size(array):
        length = 0
        for sub_array in array:
            length += len(sub_array)
        return length

    def forward(self, b):
        log_likelihood = 0
        t = self.size(b)
        alpha = numpy.zeros(len(b))

        for t in range(t):
            if t == 0:
                #Initialization
                alpha[:, t] = list(map(lambda x: x*self.prior, b[:, t]))
            else:
                #Induction
                alpha[:, t] = list(map(lambda x: numpy.transpose(self.a) * alpha[:, t - 1], b[:, t]))

            #Scaling
            alpha_sum = sum(alpha[:, t])
            alpha[:, t] = alpha[:, t] / alpha_sum
            log_likelihood += log(alpha_sum)
        return log_likelihood, alpha

    def backward(self, b):
        t = self.size(b)
        beta = numpy.zeros(len(b))

        #Initialization
        beta[:, t] = numpy.ones(len(b), 1)

        for i in range(t-1, 0, -1):
            #Induction
            beta[:, i] = self.a * (b[:, i + 1] * beta[:, i + 1])

            #Scaling
            beta[:, i] = beta[:, i] / sum(beta[:, i])
        return beta

    refactoring = '''def em_initialize(self, observations):
        #Random guessing
        self.prior = normalise(rand(self.n, 1))
        self.a = mk_stochastic(rand(self.n))

        #All states start out with the empirical diagonal covariance
        self.sigma = repmat(diag(diag(cov(numpy.transpose(observations))), [1, 1, self.n]))

        #Initialize each mean to a random data point
        indices = randperm(size(observations, 2))
        self.mu = observations[:, indices(1:self.N))

    def train(self, observations):
        self.em_initialize(observations)

        for i = 1:15:
            log_likelihood = self.em_step(observations)
            display(sprintf('Step #02d: log_likelihood = #f', i, log_likelihood))
            self.plot_gaussians(observations)

    def em_step(self, observations):
        B = self.state_likelihood(observations)
        D = size(observations, 1)
        T = size(observations, 2)

        log_likelihood, alpha = self.forward(B)
        beta = self.backward(B)

        xi_sum = zeros(self.N, self.N)
        gamma  = zeros(self.N, T)

        for t = 1:(T - 1):
            #The normalizations are done to get valid distributions for each time step
            xi_sum      = xi_sum + normalise(self.A .* (alpha[:, t) * (beta[:, t + 1) .* B[:, t + 1))'))
            gamma[:, t) = normalise(alpha[:, t) .* beta[:, t))

        gamma[:, T) = normalise(alpha[:, T) .* beta[:, T))

        expected_prior = gamma[:, 1)
        expected_A     = mk_stochastic(xi_sum)

        expected_mu    = zeros(D, self.N)
        expected_Sigma = zeros(D, D, self.N)

        gamma_state_sum = sum(gamma, 2)

        #Set any zeroes to one before dividing.
        #This forces the mean and covariance of states with probability
        #0 to become 0 instead of NaN.
        gamma_state_sum = gamma_state_sum + (gamma_state_sum == 0)

        for s = 1:self.N
            gamma_observations = observations .* repmat(gamma(s, :), [D 1])
            expected_mu[:, s)  = sum(gamma_observations, 2) / gamma_state_sum(s)

            #Make sure it's symmetric
            expected_Sigma[:, :, s) = symmetrize(gamma_observations * observations' / gamma_state_sum(s) - ...
                                                 expected_mu[:, s) * expected_mu[:, s)')

        #Ninja trick to ensure positive semidefiniteness
        expected_Sigma = expected_Sigma + repmat(0.01 * eye(D, D), [1 1 self.N])

        #M-step
        self.prior = expected_prior
        self.a     = expected_A
        self.mu    = expected_mu
        self.sigma = expected_Sigma
        return log_likelihood

    def plot_gaussians(self, observations):
        #Plotting two first dimensions

        plot(observations(1, :), observations(2, :), 'g+')
        plot(self.mu(1, :), self.mu(2, :), 'r*')

        for s = 1:size(self.Sigma, 3)
            error_ellipse(self.Sigma(1:2, 1:2, s), 'mu', self.mu(1:2, s), 'style', 'r-', 'conf', .75)

        axis([0 4000 0 4000])
        title('Training #s', self.name)
        xlabel('F1 [Hz]')
        ylabel('F2 [Hz]')'''