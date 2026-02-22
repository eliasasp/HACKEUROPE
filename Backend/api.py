from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd

# Importera din parser och din pipeline!
from monitor import format_attack_data
from main import run_cyber_risk_pipeline

app = FastAPI(title="SIG Cyber Quant API")

# Allow frontend to access this API from any origin (for demo purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# path for live-demot
TARGET_FOLDER = "hack_test"
INPUT_LOG = os.path.join(TARGET_FOLDER, "attack_table.csv")
FORMATTED_LOG = os.path.join(TARGET_FOLDER, "formatted_attacks.csv")

@app.get("/api/risk-forecast")
def get_risk_forecast():
    # 1. Parse  (10s for demo)
    format_attack_data(input_csv=INPUT_LOG, output_csv=FORMATTED_LOG, freq='10s')
    
    if not os.path.exists(FORMATTED_LOG):
        return {"status": "waiting", "message": "Väntar på attacker..."}

    try:
        # 2. Run pipeline
        # 'results' contain: lambda_history, recent_10_data, expected_attacks, etc.
        results = run_cyber_risk_pipeline(FORMATTED_LOG)
        
        if results is None:
            return {"status": "waiting", "message": "Samlar data..."}

        results["status"] = "success"
        return results

    except Exception as e:
        return {"status": "error", "message": str(e)}
