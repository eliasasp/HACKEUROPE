import numpy as np
from scipy.stats import poisson

likelihood = poisson.pmf(k=5, mu=3.2)

def log_ou_transition(x, kappa, theta, sigma, dt, z=None):
    """
    One-step transition of log-intensity.
    """
    if z is None:
        z = np.random.randn()
        
    return x + kappa * (theta - x) * dt + sigma * np.sqrt(dt) * z

def log_ou_drift(x, kappa, theta):
    return kappa * (theta - x)

def log_to_intensity(x):
    return np.exp(x)

def poisson_likelihood(n_obs, lambda_t):
    return poisson.pmf(n_obs, lambda_t)