import numpy as np
from scipy.stats import poisson
import pandas as pd
from model import log_ou_transition, log_to_intensity, poisson_likelihood

df = pd.read_csv('synthetic_ai_attack_timeseries.csv')
# Hämta bara de senaste 720 timmarna (30 dagar) för snabb och relevant analys
ys = df['attack_count'].tail(720).values

def cyber_particle_filter(ys, npart, kappa = 0.25, dt = 1.0):
    n = len(ys)
    lambda_estimates = np.zeros(n)
    
    # SÄKERHETSSPÄRR: Säkerställ att snittet (theta) aldrig är exakt 0 innan vi logaritmerar
    safe_mean = max(np.mean(ys), 0.1)
    theta_log = np.log(safe_mean)
    
    sigma = max(np.std(np.log(ys + 1.0)), 0.1) # Ändrade 1e-5 till 1.0 för stabilitet
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
    kappa = 0.25 
    lambda_estimates, final_x_particles = cyber_particle_filter(ys, npart, kappa, dt=1.0)
    
    print(f"Genomsnittlig hotnivå historiskt: {np.mean(ys):.2f}")
    print(f"Filtrets estimerade hotnivå JUST NU: {lambda_estimates[-1]:.2f}")
    print(f"Antal partiklar redo för Monte Carlo: {len(final_x_particles)}")

# Längst ner i filtering.py
if __name__ == "__main__":
    df = pd.read_csv('synthetic_ai_attack_timeseries.csv')
    ys = df['attack_count'].tail(720).values
    
    def test_filtering():
        npart = 500
        kappa = 0.25 
        lambda_estimates, final_x_particles = cyber_particle_filter(ys, npart, kappa, dt=1.0)
        
        print(f"Genomsnittlig hotnivå historiskt: {np.mean(ys):.2f}")
        print(f"Filtrets estimerade hotnivå JUST NU: {lambda_estimates[-1]:.2f}")
        print(f"Antal partiklar redo för Monte Carlo: {len(final_x_particles)}")

    test_filtering()
