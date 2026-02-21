import pandas as pd
import os

def format_attack_data(input_csv="attack_table.csv", output_csv="hourly_attacks.csv", freq='1h'):
    """
    Läser råa inloggningsförsök, filtrerar ut faktiska attacker (FAILED), 
    grupperar dem enligt angiven frekvens, och sparar i en ny CSV-fil.
    Returnerar inget.
    """
    
    # --- 1. SÄKERHETSSPÄRR OM FILEN SAKNAS ---
    if not os.path.exists(input_csv):
        print(f"[!] Hittade inte {input_csv}. Skapar en tom mall.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return

    # --- 2. LÄS IN FILEN (Hantera om den är helt tom) ---
    try:
        # Vi säger åt Pandas att det inte finns någon rubrikrad (header=None), 
# och tvingar sedan namnen på kolumnerna manuellt.
        df = pd.read_csv(input_csv, header=None, names=['timestamp', 'ip', 'user', 'password', 'status'])
    except pd.errors.EmptyDataError:
        print("[!] CSV-filen är helt tom. Skapar en tom mall.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return
        
    if len(df) == 0:
        print("[!] CSV-filen saknar rader. Skapar en tom mall.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return

    # --- 3. IDIOTSÄKER KOLUMN-FORMATERING ---
    # Gör alla kolumnnamn till små bokstäver och ta bort mellanslag. 
    # Fixar KeyError direkt!
    df.columns = df.columns.str.strip().str.lower()

    # --- 4. FILTRERA PÅ FAILED ---
    if 'status' in df.columns:
        # Gör 'FAILED' till stora bokstäver i kollen, oavsett hur det loggades
        df = df[df['status'].astype(str).str.upper() == 'FAILED'].copy()

    if len(df) == 0:
        print("[!] Inga 'FAILED'-attacker hittades än. Skapar en tom mall.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return

    # --- 5. FORMATERA OCH GRUPPERA (Resample) ---
    # Nu VET vi att kolumnen heter 'timestamp' med litet t
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    counts = df.resample(freq).size().fillna(0).astype(int)
    
    output_df = pd.DataFrame({
        'timestamp': counts.index.strftime('%Y-%m-%d %H:%M:%S'),
        'attack_count': counts.values
    })

    # Skapar filen och avslutar funktionen tyst och snyggt!
    output_df.to_csv(output_csv, index=False)
    print(f"[+] Succé! Sparade {len(output_df)} formaterade rader till {output_csv}")