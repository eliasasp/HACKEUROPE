import requests
import time
import random

# Inställningar
TARGET_URL = "http://127.0.0.1:5000/login"
LAMBDA = 5  # Genomsnittligt antal attacker per minut
ATTACK_DURATION_MINUTES = 2

def run_attack():
    print(f"Startar attack-simulering (Poisson-process, λ={LAMBDA})...")
    start_time = time.time()
    end_time = start_time + (ATTACK_DURATION_MINUTES * 60)
    
    total_attempts = 0

    while time.time() < end_time:
        # Beräkna nästa väntetid baserat på Poisson-processen (exponentialfördelning)
        # Väntetid = -ln(U) / λ, där U är ett slumptal mellan 0 och 1
        wait_time = random.expovariate(LAMBDA / 60) 
        time.sleep(wait_time)
        
        # Utför "hacket"
        try:
            payload = {'user': 'admin', 'pass': 'password123'}
            requests.post(TARGET_URL, data=payload)
            total_attempts += 1
            print(f"Attack {total_attempts} utförd efter {wait_time:.2f}s vila.")
        except Exception as e:
            print(f"Kunde inte nå servern: {e}")

    print(f"Simulering klar. Totalt antal försök: {total_attempts}")

if __name__ == "__main__":
    run_attack()