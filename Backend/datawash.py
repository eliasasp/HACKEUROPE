import pandas as pd

def format_to_minutely_csv(input_path="AWS_Honeypot_marx-geo.csv", output_path="formatted_minutely.csv"):
    print(f"[*] Läser in rådata från {input_path}...")
    
    try:
        df = pd.read_csv(input_path, usecols=['datetime'])
    except Exception as e:
        print(f"[-] Fel vid inläsning: {e}")
        return

    # 2. convert to datum-objekt
    # '3/3/13 21:53' is %m/%d/%y %H:%M
    print("[*] Convert time stamlpe...")
    df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%y %H:%M')
    
    # 3. Sort
    df = df.sort_values('datetime')

    # 4. Resample to minutely counts
    minutely_df = df.set_index('datetime').resample('1h').size().to_frame(name='attack_count')
    
    # Get index for timestamp and attack_count
    minutely_df = minutely_df.reset_index()
    minutely_df.columns = ['timestamp', 'attack_count']

    # 5. save to new CSV
    minutely_df.to_csv(output_path, index=False)
    
    print(minutely_df.head())

if __name__ == "__main__":
    format_to_minutely_csv("AWS_Honeypot_marx-geo.csv")