import pandas as pd
import numpy as np

# Importera era egna moduler!
# (Förutsätter att du sparat funktionerna i filter.py och forecaster.py)
from filtering import cyber_particle_filter
from MC_simulation import ThreatForecaster

def run_cyber_risk_pipeline(csv_path):
    print("--- STARTAR CYBER-QUANT PIPELINE ---")
    
    # 1. LÄS IN DATA
    print(f"Laddar data från {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Använd rullande fönster (senaste 30 dagarna) för snabbhet och relevans
    ys = df['attack_count'].tail(720).values
    
    # 2. DATADRIVEN KALIBRERING (Låter datan styra parametrarna)
    theta_val = np.log(np.mean(ys) + 1e-6)
    raw_sigma = np.std(np.log(ys + 1.0))
    sigma_val = min(raw_sigma, 0.5)
    kappa_val = 0.25
    n_particles = 500
    
    # 3. KÖR PARTIKELFILTRET (Hitta sanningen i dåtiden)
    print("Kör Sequential Monte Carlo (SISR) för att estimera latent hotnivå...")
    lambda_estimates, final_log_particles = cyber_particle_filter(
        ys, 
        npart=n_particles, 
        kappa=kappa_val, 
        dt=1.0
    )
    current_lambda = lambda_estimates[-1]
    print(f"-> Estimerad hotnivå just nu: {current_lambda:.2f} attacker/timme")
    
    # 4. KÖR FRAMTIDSPROGNOSEN (Monte Carlo in i framtiden)
    print("Kör Monte Carlo-simuleringar för de kommande 24 timmarna...")
    forecaster = ThreatForecaster(kappa=kappa_val, theta=theta_val, sigma=sigma_val)
    
    # 2000 parallella universum, 24 timmar framåt
    results = forecaster.simulate(log_particles=final_log_particles, steps=24, n_sim=2000)
    attack_paths = results["attack_paths"]
    
    # 5. RISK METRICS
    total_attacks_per_sim = np.sum(attack_paths, axis=1)

    expected_attacks = float(np.mean(total_attacks_per_sim))
    worst_case_95 = float(np.percentile(total_attacks_per_sim, 95))
    worst_case_99 = float(np.percentile(total_attacks_per_sim, 99))

    critical_threshold = np.mean(ys) * 1.8

    prob_escalation = float(
        np.mean(np.max(attack_paths, axis=1) > critical_threshold)
    )

    print("\n--- RESULTAT: 24H FORECAST ---")
    print(f"Förväntat antal attacker:     {expected_attacks:.0f} st")
    print(f"Worst-Case (95% konfidens):   {worst_case_95:.0f} st")
    print(f"Black Swan (99% konfidens):   {worst_case_99:.0f} st")
    print(f"Escalation probability:       {prob_escalation:.2%}")
    print("------------------------------------")

    return {
        "current_lambda": float(current_lambda),
        "lambda_estimates": lambda_estimates.tolist(),
        "attack_paths": attack_paths.tolist(),
        "expected_attacks": expected_attacks,
        "worst_case_95": worst_case_95,
        "worst_case_99": worst_case_99,
        "prob_escalation": prob_escalation
    }


# Standard Python-mönster för att köra scriptet
if __name__ == "__main__":
    # Byt ut namnet till din faktiska CSV-fil
    run_cyber_risk_pipeline('synthetic_ai_attack_timeseries.csv')