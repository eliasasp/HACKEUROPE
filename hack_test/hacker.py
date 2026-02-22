import requests
import time
import random

# --- INSTÄLLNINGAR ---
TARGET_URL = "http://127.0.0.1:5000/login"
LAMBDA = 55  # Snitt på 15 inloggningsförsök per minut
ATTACK_DURATION_MINUTES = 10  # Hur länge scriptet ska köra

# Listor med fiktiva uppgifter för att göra loggen realistisk
USERNAMES = ["admin", "root", "user", "test", "administrator", "guest", "info"]
PASSWORDS = ["123456", "password", "admin123", "qwerty", "111111", "welcome", "letmein"]

def run_brute_force():
    print(f"[*] Startar simulerad Brute Force-attack mot {TARGET_URL}")
    print(f"[*] Metod: Poisson-process (λ={LAMBDA} attacker/min)")
    
    start_time = time.time()
    end_time = start_time + (ATTACK_DURATION_MINUTES * 60)
    total_attempts = 0

    while time.time() < end_time:
        # Beräkna väntetid med exponentialfördelning (Poisson)
        wait_time = random.expovariate(LAMBDA / 60)
        time.sleep(wait_time)
        
        # Slumpa fram ett användarnamn och lösenord från listorna
        test_user = random.choice(USERNAMES)
        test_pass = random.choice(PASSWORDS)
        
        # Skapa datan som ska skickas (måste matcha namnen i HTML-formuläret)
        payload = {
            'user': test_user,
            'pass': test_pass
        }
        
        try:
            # Utför POST-anropet (själva inloggningsförsöket)
            response = requests.post(TARGET_URL, data=payload)
            total_attempts += 1
            
            # Status 401 betyder "Unauthorized", vilket är vad vår server returnerar vid fel
            if response.status_code == 401:
                print(f"[ATTACK {total_attempts}] Testade: {test_user}:{test_pass} -> Blockerad (Väntar {wait_time:.2f}s)")
            else:
                print(f"[ATTACK {total_attempts}] Testade: {test_user}:{test_pass} -> Oväntat svar: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("[!] Kunde inte ansluta. Är servern (server.py) igång?")
            time.sleep(2) # Pausa lite om servern är nere

    print(f"\n[*] Attack-simulering avslutad. Totalt {total_attempts} försök utfördes.")

if __name__ == "__main__":
    run_brute_force()