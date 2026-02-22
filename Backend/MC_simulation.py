import numpy as np
from model import log_ou_transition, log_to_intensity

class ThreatForecaster:

    def __init__(self, kappa, theta, sigma, dt=1.0):
        self.kappa = kappa
        safe_theta = max(theta, 0.1)
        self.theta_log = np.log(safe_theta)
        self.sigma = sigma
        self.dt = dt

    def simulate(self, log_particles, steps=24, n_sim=2000):
        """
        RUN  (Monte Carlo) of cyber attacks
         - log_particles: Log-lambda particle
        """

        x = np.random.choice(log_particles, size=n_sim)

        # Matriser för att spara hela tidslinjen (n_sim rader, steps kolumner)
        lambda_paths = np.zeros((n_sim, steps))
        attack_paths = np.zeros((n_sim, steps))

        for t in range(steps):
            
            # Dra standardnormalfördelat brus för alla simuleringar
            z = np.random.randn(n_sim)

            # Stega framåt med Log-OU processen
            x = log_ou_transition(
                x,
                self.kappa,
                self.theta_log,
                self.sigma,
                self.dt,
                z=z
            )

            # Konvertera log(lambda) till faktisk lambda
            lambda_t = log_to_intensity(x)

            # Spara intensiteten
            lambda_paths[:, t] = lambda_t
            
            # Dra faktiska antalet attacker via Poisson-fördelning och spara
            attack_paths[:, t] = np.random.poisson(lambda_t)

        return {
            "lambda_paths": lambda_paths,
            "attack_paths": attack_paths
        }
    
