import pandas as pd

def format_to_minutely_csv(input_path="AWS_Honeypot_marx-geo.csv", output_path="formatted_minutely.csv"):
    print(f"[*] Läser in rådata från {input_path}...")
    
    # 1. Läs in datan (vi behöver bara datetime-kolumnen)
    try:
        df = pd.read_csv(input_path, usecols=['datetime'])
    except Exception as e:
        print(f"[-] Fel vid inläsning: {e}")
        return

    # 2. Konvertera till datum-objekt
    # Formatet '3/3/13 21:53' motsvarar %m/%d/%y %H:%M
    print("[*] Konverterar tidsstämplar...")
    df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%y %H:%M')
    
    # 3. Sortera kronologiskt
    df = df.sort_values('datetime')

    # 4. Aggregera per minut
    # Vi sätter datetime som index och räknar rader per minut ('1min')
    print("[*] Grupperar data per minut och fyller i luckor med nollor...")
    minutely_df = df.set_index('datetime').resample('1h').size().to_frame(name='attack_count')
    
    # Återställ index för att få 'timestamp' som en kolumn igen
    minutely_df = minutely_df.reset_index()
    minutely_df.columns = ['timestamp', 'attack_count']

    # 5. Spara till ny CSV
    minutely_df.to_csv(output_path, index=False)
    
    print(f"[+] Succé! Sparade {len(minutely_df)} rader till {output_path}")
    print(minutely_df.head())

if __name__ == "__main__":
    # Se till att filnamnet matchar din fil på datorn
    format_to_minutely_csv("AWS_Honeypot_marx-geo.csv")