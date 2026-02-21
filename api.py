from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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
    # 1. Be log_parser formatera rådatan från webbservern
    # (Använd '10s' för live-demot så det går undan!)
    format_attack_data(input_csv=INPUT_LOG, output_csv=FORMATTED_LOG, freq='10s')
    
    # 2. Kontrollera att filen faktiskt skapades
    if not os.path.exists(FORMATTED_LOG):
        return {"status": "waiting", "message": "Väntar på attacker från servern..."}

    try:
        # 3. KÖR DIN BEFINTLIGA PIPELINE!
        results = run_cyber_risk_pipeline(FORMATTED_LOG)
        
        # Om pipelinen kraschar för att vi har för lite data än (mindre än 2 rader)
        if results is None:
            return {"status": "waiting", "message": "Samlar in tillräckligt med data..."}

        # 4. Skicka din dictionary direkt till Lovable/React
        return {
            "status": "success",
            "data": results 
        }

    except Exception as e:
        return {"status": "error", "message": f"Kritiskt fel i pipelinen: {str(e)}"}