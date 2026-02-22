import pandas as pd
import numpy as np
from filtering import cyber_particle_filter
from MC_simulation import ThreatForecaster

def run_cyber_risk_pipeline(csv_path):
    print(f"Laddar data från {csv_path}...")
    df = pd.read_csv(csv_path)

    # --- LÖSNING PÅ RIGHT-EDGE PROBLEMET ---
    # 10-sekundersfönstret fortfarande håller på att fyllas i realtid.
    if len(df) > 1:
        df = df.iloc[:-1] 
    # ---------------------------------------

    # --- Rullande 10-minutersfönster ---
    recent_10_df = df.tail(10)
    if len(recent_10_df) > 0:
        recent_10_data = recent_10_df[['timestamp', 'attack_count']].to_dict(orient='records')
        recent_10_avg = float(recent_10_df['attack_count'].mean())
    else:
        recent_10_data = []
        recent_10_avg = 0.0
    
    # Använd rullande fönster (senaste 30 dagarna) för snabbhet och relevans
    ys = df['attack_count'].tail(720).values

    # --- SAFETY CATCH (om filen är tom vid uppstart) ---
    if len(ys) == 0:
        print("[!] Filen är tom. Väntar på inkommande data från hacker.py...")
        return {
            "current_lambda": 0.0,
            "chart_data": [],        
            "expected_attacks": 0.0,
            "worst_case_95": 0.0,
            "prob_escalation": 0.0,
            "recent_10_avg": 0.0        
        }
    # ----------------------------------------------------
    
    # 2. DATADRIVEN KALIBRERING (Låter datan styra parametrarna)
    theta_val = np.log(np.mean(ys) + 1e-6)
    raw_sigma = np.std(np.log(ys + 1.0))
    sigma_val = min(raw_sigma, 0.5)
    kappa_val = 0.05
    n_particles = 500
    
    # 3. KÖR PARTIKELFILTRET (Hitta sanningen i dåtiden)
    lambda_estimates, final_log_particles = cyber_particle_filter(
        ys, 
        npart=n_particles, 
        kappa=kappa_val, 
        dt=1.0
    )
    current_lambda = lambda_estimates[-1]
    print(f"-> Estimerad hotnivå just nu: {current_lambda:.2f} attacker/tidsenhet")
    
    # 4. KÖR FRAMTIDSPROGNOSEN (Monte Carlo in i framtiden)
    forecaster = ThreatForecaster(kappa=kappa_val, theta=theta_val, sigma=sigma_val)
    
    # 2000 parallella universum, 24 steg framåt
    results = forecaster.simulate(log_particles=final_log_particles, steps=24, n_sim=2000)
    attack_paths = results["attack_paths"]
    
    # 5. RISK METRICS
    total_attacks_per_sim = np.sum(attack_paths, axis=1)

    expected_attacks = float(np.mean(total_attacks_per_sim))
    worst_case_95 = float(np.percentile(total_attacks_per_sim, 95))
    worst_case_99 = float(np.percentile(total_attacks_per_sim, 99))

    stat_threshold = np.mean(ys) + (3 * np.std(ys))
    
    # 2. Vi sätter en absolut gräns: Minst 50% värre än den nuvarande hotnivån
    intensity_threshold = current_lambda * 1.5
    
    # 3. Tröskelvärdet blir det högsta av dessa två. 
    # Vi lägger också till ett "golv" (t.ex. 10) så att modellen inte ropar varg 
    # bara för att attackerna ökar från 1 till 2 st.
    critical_threshold = max(stat_threshold, intensity_threshold, 10.0)

    prob_escalation = float(
        np.mean(np.max(attack_paths, axis=1) > critical_threshold)
    )

    # --- NYTT: SKAPA EN PERFEKT KRONOLOGISK GRAF-ARRAY ---
    # 1. Hämta de senaste 15 datapunkterna för snygg historik
    chart_len = 15
    hist_df = df.tail(chart_len)
    
    t_list = hist_df['timestamp'].tolist()
    a_list = hist_df['attack_count'].tolist()
    # Säkerställ att vi tar exakt lika många lambda-värden som vi har rader
    l_list = lambda_estimates[-len(hist_df):] 
    
    unified_chart_data = []
    for t, a, l in zip(t_list, a_list, l_list):
        # Formatera tiden snyggt till HH:MM:SS
        t_str = str(t).split()[-1] if " " in str(t) else str(t)
        unified_chart_data.append({
            "timestamp": t_str,
            "actual_attacks": int(a),
            "lambda_val": round(float(l), 2),
            "predicted_attacks": None # Finns inget predikterat i dåtiden
        })
        
    # 2. LÄGG TILL EXAKT ETT FRAMTIDSSTEG (Prognos)
    # Vi plockar ut steg 1 (nästa tidsenhet) från alla dina 2000 simulerade universum
    step_1_sims = attack_paths[:, 0]
    next_expected = float(np.mean(step_1_sims))
    
    # Lägg till prognosen i slutet av grafen!
    unified_chart_data.append({
        "timestamp": "Prognos",
        "actual_attacks": None,  # Framtiden har inget facit än
        "lambda_val": None,      # Filtreringen är inte klar för framtiden
        "predicted_attacks": round(next_expected, 2)
    })
    # -----------------------------------------------------

    return {
        "current_lambda": float(current_lambda),
        "chart_data": unified_chart_data,  # <-- Skickar vår nya perfekta array!
        
        # Behåll resten så KPI-korten fungerar
        "expected_attacks": expected_attacks,
        "worst_case_95": worst_case_95,
        "prob_escalation": prob_escalation,
        "recent_10_avg": recent_10_avg
    }