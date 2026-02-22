import pandas as pd
import os

def format_attack_data(input_csv="attack_table.csv", output_csv="hourly_attacks.csv", freq='1h'):
    """
    Reads raw login attempts, filters out actual attacks (FAILED), 
    groups them according to the specified frequency, and saves them to a new CSV file.
    Returns nothing.
    """
    
    # --- 1. FAILSAFE IF THE FILE IS MISSING ---
    if not os.path.exists(input_csv):
        print(f"[!] Could not find {input_csv}. Creating an empty template.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return

    # --- 2. LOAD THE FILE (Handle completely empty files) ---
    try:
        # We tell Pandas there is no header row (header=None), 
        # and then manually force the column names.
        df = pd.read_csv(input_csv, header=None, names=['timestamp', 'ip', 'user', 'password', 'status'])
    except pd.errors.EmptyDataError:
        print("[!] The CSV file is completely empty. Creating an empty template.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return
        
    if len(df) == 0:
        print("[!] The CSV file has no rows. Creating an empty template.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return

    # --- 3. FOOLPROOF COLUMN FORMATTING ---
    # Convert all column names to lowercase and strip whitespace. 
    # This prevents KeyErrors immediately!
    df.columns = df.columns.str.strip().str.lower()

    # --- 4. FILTER FOR FAILED ATTEMPTS ---
    if 'status' in df.columns:
        # Force the status check to uppercase 'FAILED', regardless of how it was originally logged
        df = df[df['status'].astype(str).str.upper() == 'FAILED'].copy()

    if len(df) == 0:
        print("[!] No 'FAILED' attacks found yet. Creating an empty template.")
        pd.DataFrame(columns=['timestamp', 'attack_count']).to_csv(output_csv, index=False)
        return

    # --- 5. FORMAT AND GROUP (Resample) ---
    # Now we KNOW the column is definitively named 'timestamp' with a lowercase 't'
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Count the number of attacks per time window
    counts = df.resample(freq).size().fillna(0).astype(int)
    
    output_df = pd.DataFrame({
        'timestamp': counts.index.strftime('%Y-%m-%d %H:%M:%S'),
        'attack_count': counts.values
    })

    # Create the file and exit the function cleanly!
    output_df.to_csv(output_csv, index=False)
    print(f"[+] Success! Saved {len(output_df)} formatted rows to {output_csv}")