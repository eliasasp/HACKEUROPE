import numpy as np
from scipy.stats import poisson
import pandas as pd
from model import log_ou_transition, log_to_intensity, poisson_likelihood

df = pd.read_csv('synthetic_ai_attack_timeseries.csv')
ys = df['attack_count'].values

def cyber_particle_filter(ys, npart, kappa = 0.25, dt = 1.0):
    """
    ys: Array med faktiska antalet attacker/alerts per tidssteg (t.ex. per timme)
    npart: Antal partiklar (t.ex. 500 eller 1000)
    drift_std: Hur mycket vi tillåter den dolda hotnivån att ändras per tidssteg
    """
    n = len(ys)
    lambda_estimates = np.zeros(n)
    theta_log = np.log(np.mean(ys))
    sigma = max(np.std(np.log(ys + 1e-5)), 0.1)
    
    # 1. INITIALISERING
    # Istället för C och D från labben, gissar vi en start-intensitet (lambda).
    # Lambda måste vara > 0.
    lam_init = np.random.uniform(0.1, np.max(ys) + 1, size=npart) 
    x_particle = np.log(lam_init)  # x represents ln(lambda)
    
    weights = np.zeros(npart)
    
    for i in range(n):
        if i > 0:
            # RÄTTELSE: Använd randn (Standard Normal) för stokastiskt brus!
            z_array  = np.random.randn(npart)
            
            # Skicka in arrayen i log-OU-processen
            x_particle = log_ou_transition(x_particle, kappa, theta_log, sigma, dt, z_array)

        # Collect the real intensity from the log-OU process
        lam_particle = log_to_intensity(x_particle)

        # The actual likelihood
        weights = poisson_likelihood(ys[i], lam_particle)
        
        # Normalisera vikterna
        if np.sum(weights) == 0:
            weights[:] = 1.0 / npart
        else:
            weights /= np.sum(weights)
            
        # 4. RESAMPLING SISR - filtering
        idx = np.random.choice(npart, size=npart, replace=True, p=weights)
        
        # Kloning av de bra partiklarna och borttagning av de dåliga
        x_particle = x_particle[idx]
        
        # 5. Save the estimate
        # Convert to real intensity and not log(intensity)
        resampled_lam = log_to_intensity(x_particle)
        lambda_estimates[i] = np.mean(resampled_lam)
        #transformera till log!!
        
    return lambda_estimates, x_particle

def test_filtering():
    npart = 500
    kappa = 0.25 #motivera mer sen- mean reversion speed (hur fort vi återgår till det normala värdet efter en attackvåg)
    lambda_estimates, x_particle = cyber_particle_filter(ys, npart, kappa, dt = 1.0)
    print(lambda_estimates)

test_filtering()
