import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import sys
# Lägger till mappen ovanför i Pythons söklista
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import cyber_particle_filter, ThreatForecaster
# Vi importerar logiken direkt från din main-fil
from main import cyber_particle_filter, ThreatForecaster

def run_backtest_with_main_logic(csv_path="AWS_Honeypot_marx-geo.csv"):
    print("[*] Initierar Backtest: Använder logik från main.py")
    
    # 1. FÖRBERED DATA
    df_raw = pd.read_csv(csv_path)
    # Matchar ditt nya format: 3/3/13 21:53
    df_raw['datetime'] = pd.to_datetime(df_raw['datetime'], format='%m/%d/%y %H:%M')
    df_raw = df_raw.sort_values('datetime')
    
    # Aggregera per minut (räkna rader)
    ts = df_raw.set_index('datetime').resample('1min').size().to_frame(name='attack_count')
    
    if len(ts) < 2000:
        print(f"[!] Datasetet för kort ({len(ts)} min). Behöver 2000+ för 1000/1000 split.")
        return

    # Inställningar för backtestet
    burn_in = 1000
    test_range = 1000
    results = []

    print(f"[*] Kör rullande fönster över {test_range} minuter...")

    # LOOP: Vi simulerar att vi står vid varje minut 'i' och förutspår framtiden
    for i in range(burn_in, burn_in + test_range):
        # Ta de senaste 720 observationerna (precis som din main.py gör med .tail(720))
        window = ts.iloc[i-720 : i]
        ys = window['attack_count'].values
        
        # --- EXAKT SAMMA LOGIK SOM I main.py ---
        theta_val = np.log(np.mean(ys) + 1e-6)
        raw_sigma = np.std(np.log(ys + 1.0))
        sigma_val = min(raw_sigma, 0.5)
        kappa_val = 0.25
        n_particles = 500
        
        # 1. Kör filtret (SISR)
        # Vi behöver log_particles för att mata forecastern
        _, final_log_particles = cyber_particle_filter(
            ys, npart=n_particles, kappa=kappa_val, dt=1.0
        )
        
        # 2. Kör Prognosen (Monte Carlo)
        # Vi kollar 60 minuter framåt istället för 24h eftersom vi kör minut-data
        forecaster = ThreatForecaster(kappa=kappa_val, theta=theta_val, sigma=sigma_val)
        sim_results = forecaster.simulate(log_particles=final_log_particles, steps=60, n_sim=1000)
        
        # 3. EXTRAHERA RISK-METRICS
        attack_paths = sim_results["attack_paths"]
        expected_next_hour = np.mean(np.sum(attack_paths, axis=1))
        worst_case_95 = np.percentile(np.sum(attack_paths, axis=1), 95)
        
        # Jämför med facit (vad hände faktiskt de kommande 60 minuterna?)
        actual_outcome = ts.iloc[i : i+60]['attack_count'].sum()

        results.append({
            'timestamp': ts.index[i],
            'actual': actual_outcome,
            'expected': expected_next_hour,
            'worst_case': worst_case_95
        })

        if (i - burn_in) % 100 == 0:
            print(f"  > Framsteg: {i - burn_in}/{test_range} minuter klara...")

    # --- PLOTTA RESULTATET ---
    res_df = pd.DataFrame(results).set_index('timestamp')
    
    plt.figure(figsize=(15, 8))
    plt.plot(res_df.index, res_df['actual'], label='Faktiskt utfall (Nästa 60 min)', color='#2c3e50', alpha=0.4)
    plt.plot(res_df.index, res_df['expected'], label='Main-Pipeline Prognos', color='#e74c3c', linewidth=2)
    plt.fill_between(res_df.index, res_df['expected'], res_df['worst_case'], 
                     color='#e74c3c', alpha=0.2, label='95% Konfidens (Riskspann)')
    
    plt.title('Backtesting av Main Pipeline: Minut-för-minut validering', fontsize=14)
    plt.ylabel('Antal attacker (Aggregerat 60 min)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

    # Beräkna hur ofta vi "sprängde" vår riskmodell
    hits = sum(1 for a, w in zip(res_df['actual'], res_df['worst_case']) if a <= w)
    print(f"\n[+] Backtest slutfört!")
    print(f"[+] Modellens tillförlitlighet: {(hits/test_range)*100:.2f}%")

if __name__ == "__main__":
    run_backtest_with_main_logic()