import numpy as np
from scipy.stats import poisson
import pandas as pd

df = pd.read_csv('synthetic_ai_attack_timeseries.csv')
ys = df['attack_count'].values

def cyber_particle_filter(ys, npart, drift_std=0.1):
    """
    ys: Array med faktiska antalet attacker/alerts per tidssteg (t.ex. per timme)
    npart: Antal partiklar (t.ex. 500 eller 1000)
    drift_std: Hur mycket vi tillåter den dolda hotnivån att ändras per tidssteg
    """
    n = len(ys)
    lambda_estimates = np.zeros(n)
    
    # 1. INITIALISERING
    # Istället för C och D från labben, gissar vi en start-intensitet (lambda).
    # Lambda måste vara > 0.
    lam = np.random.uniform(0.1, np.max(ys) + 1, size=npart) 
    
    weights = np.zeros(npart)
    
    for i in range(n):
        # 2. TILLSTÅNDSMODELL (Hur hotnivån utvecklas)
        if i > 0:
            # Istället för populationstillväxt använder vi en "Log-normal Random Walk".
            # Detta låter hotnivån driva slumpmässigt upp/ner, men garanterar att den aldrig blir negativ.
            lam = lam * np.exp(np.random.normal(0, drift_std, size=npart))
        
        # 3. LIKELIHOOD (Hur bra gissade partikeln?)
        # Byt ut din gamla 'valid' och 'lower_bound' mot Poissons sannolikhetsfunktion (PMF).
        # pmf = "Givet intensiteten 'lam', hur stor är chansen att exakt ys[i] attacker skedde?"
        weights = poisson.pmf(ys[i], lam)
        
        # Normalisera vikterna (Exakt samma säkerhetsspärr som i din kod)
        if np.sum(weights) == 0:
            weights[:] = 1.0 / npart
        else:
            weights /= np.sum(weights)
            
        # 4. RESAMPLING (Din exakta logik från labben!)
        idx = np.random.choice(npart, size=npart, replace=True, p=weights)
        
        # Kloning av de bra partiklarna och borttagning av de dåliga
        lam = lam[idx]
        
        # 5. ESTIMATET FÖR DETTA TIDSSTEG
        # Spara medelvärdet av de överlevande partiklarna som vår skattade hotnivå
        lambda_estimates[i] = np.mean(lam)
        
    return lambda_estimates

lambda_estimates = cyber_particle_filter(ys, npart=1000, drift_std=0.1)
print(lambda_estimates)