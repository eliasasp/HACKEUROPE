import numpy as np
from model import log_ou_transition, log_to_intensity


class ThreatForecaster:

    def __init__(self, kappa, theta, sigma, dt):
        self.kappa = kappa
        self.theta = theta
        self.sigma = sigma
        self.dt = dt

    def simulate(
        self,
        lambda_estimates,
        steps=24,
        n_sim=2000
    ):
        """
        Run forward Monte Carlo simulation.
        """

        # Sample initial log-intensity
        x = np.random.choice(lambda_estimates, size=n_sim)

        lambda_paths = np.zeros((n_sim, steps))
        attack_paths = np.zeros((n_sim, steps))

        for t in range(steps):

            x = log_ou_transition(
                x,
                self.kappa,
                self.theta,
                self.sigma,
                self.dt
            )

            lambda_t = log_to_intensity(x)

            lambda_paths[:, t] = lambda_t
            attack_paths[:, t] = np.random.poisson(lambda_t)

        return {
            "lambda_paths": lambda_paths,
            "attack_paths": attack_paths
        }
