import os
from monitor import format_attack_data
from main import run_cyber_risk_pipeline

def interactive_demo():
    print("="*60)
    print("🚀 CYBER RISK DASHBOARD - BACKEND CONTROLLER")
    print("="*60)
    print("Instruktioner:")
    print("1. Starta 'python server.py' i Terminal 1.")
    print("2. Starta 'python hacker.py' i Terminal 2.")
    print("3. Tryck på [ENTER] här för att simulera en frontend-knapp!\n")

    # VIKTIGT: Här pekar vi nu ut mappen "hack_test"
    target_folder = "hack_test"
    
    # Skapa mappen automatiskt om den mot förmodan saknas
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Bygg de fullständiga sökvägarna: t.ex. "hack_test/attack_table.csv"
    input_log = os.path.join(target_folder, "attack_table.csv")
    formatted_log = os.path.join(target_folder, "formatted_attacks.csv")

    while True:
        cmd = input("Tryck [ENTER] för att hämta ny riskestimering (eller 'q' för att avsluta): ")
        if cmd.lower() == 'q':
            break

        print("\n[+] Knapptryck mottaget! Parsar loggar...")

        # 1. Bygg filen via log_parser
        # Vi skickar in de nya sökvägarna med mappen inkluderad!
        format_attack_data(input_csv=input_log, output_csv=formatted_log, freq='10s')

        # 2. SÄKERHETSSPÄRR: Kontrollera om filen faktiskt skapades i hack_test
        if not os.path.exists(formatted_log):
            print(f"[-] Kunde inte hitta eller skapa formaterad data i {target_folder}.")
            print("[-] Tips: Har du startat server.py och låtit hacker.py köra i några sekunder?\n")
            continue

        # 3. Kör de tunga beräkningarna
        print("[+] Data formaterad. Kör SMC-filter och Monte Carlo...")
        estimations = run_cyber_risk_pipeline(formatted_log)

        if estimations is None:
            print("[-] Ett fel uppstod i beräkningen. (Kanske för få inloggningsförsök än?)\n")
            continue

        # 4. Presentera resultaten
        print("\n" + "-"*40)
        print("📊 ESTIMERINGAR TILL FRONTEND")
        print("-"*40)
        print(f"Hotnivå just nu (Lambda): {estimations['current_lambda']:>7.2f}")
        print(f"Förväntat antal attacker: {estimations['expected_attacks']:>7.0f}")
        print(f"Worst-Case (95% VaR):     {estimations['worst_case']:>7.0f}")
        print("-"*40 + "\n")

if __name__ == "__main__":
    interactive_demo()