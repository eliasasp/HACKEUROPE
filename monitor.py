import pandas as pd
import os

def format_attack_data(input_csv="attack_table.csv", output_csv="hourly_attacks.csv", freq='1h'):
    """
    Läser råa inloggningsförsök, filtrerar ut faktiska attacker (FAILED), 
    grupperar dem enligt angiven frekvens, och sparar i en ny CSV-fil.
    Returnerar inget.
    """
    print(f"[*] Läser in rådata från {input_csv}...")
    
    if not os.path.exists(input_csv):
        print(f"[!] Hittade inte {input_csv}.")
        return

    df = pd.read_csv(input_csv)
    
    if len(df) == 0:
        print("[!] CSV-filen är tom.")
        return

    if 'Status' in df.columns:
        df = df[df['Status'] == 'FAILED'].copy()

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)
    
    counts = df.resample(freq).size().fillna(0).astype(int)
    
    output_df = pd.DataFrame({
        'timestamp': counts.index.strftime('%Y-%m-%d %H:%M:%S'),
        'attack_count': counts.values
    })

    # Skapar filen och avslutar funktionen tyst och snyggt!
    output_df.to_csv(output_csv, index=False)
    print(f"[+] Succé! Sparade {len(output_df)} formaterade rader till {output_csv}")
