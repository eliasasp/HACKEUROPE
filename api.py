from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
# Importera din parser och din pipeline!
from monitor import format_attack_data
from main import run_cyber_risk_pipeline  # Byt ut 'main' mot vad filen faktiskt heter

app = FastAPI(title="SIG Cyber Quant API")

# Tillåt frontenden att hämta data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sökvägar för live-demot
TARGET_FOLDER = "hack_test"
INPUT_LOG = os.path.join(TARGET_FOLDER, "attack_table.csv")
FORMATTED_LOG = os.path.join(TARGET_FOLDER, "formatted_attacks.csv")

@app.get("/api/risk-forecast")
def get_risk_forecast():
    # 1. Parsa rådatan (10s för demo)
    format_attack_data(input_csv=INPUT_LOG, output_csv=FORMATTED_LOG, freq='10s')
    
    if not os.path.exists(FORMATTED_LOG):
        return {"status": "waiting", "message": "Väntar på attacker..."}

    try:
        # 2. Kör din pipeline
        results = run_cyber_risk_pipeline(FORMATTED_LOG)
        
        if results is None:
            return {"status": "waiting", "message": "Samlar data..."}

        # 3. Läs in de faktiska attack-staplarna (ys) för att skicka med dem till grafen
        # (Detta gör att frontenden kan visa både staplar och linjen)
        df_temp = pd.read_csv(FORMATTED_LOG)
        
        # 4. Formatera svaret för Lovable
        return {
            "status": "success",
            "historical_data": {
                # Vi tar bara tiden (HH:MM:SS) för snyggare X-axel
                "timestamps": [t.split(" ")[1] for t in df_temp['timestamp'].tolist()],
                "actual_attacks": df_temp['attack_count'].tolist(),
                "estimated_lambda": results["lambda_estimates"]
            },
            "forecast": {
                "current_threat_level": round(results["current_lambda"], 2),
                "expected_attacks_next_window": round(results["expected_attacks"], 1),
                "worst_case_95_percentile": round(results["worst_case_95"], 1),
                "prob_escalation": round(results["prob_escalation"] * 100, 1) # Procent
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
