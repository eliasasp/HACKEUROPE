from flask import Flask, request, render_template_string
import datetime
import csv
import os

app = Flask(__name__)
LOG_FILE = 'attack_table.csv'

# 1. Skapa CSV-filen (tabellen) om den inte redan finns
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'IP_Address', 'Username', 'Password_Used', 'Status'])

# 2. HTML-mallen för en snygg inloggningssida
LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Portal</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px; }
        .login-box h2 { margin-top: 0; color: #333; text-align: center; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; margin-bottom: 5px; color: #666; }
        .input-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        .btn { width: 100%; padding: 10px; background-color: #0056b3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .btn:hover { background-color: #004494; }
        .error { color: red; text-align: center; margin-top: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Admin Portal</h2>
        <form method="POST" action="/login">
            <div class="input-group">
                <label for="user">Användarnamn</label>
                <input type="text" id="user" name="user" required>
            </div>
            <div class="input-group">
                <label for="pass">Lösenord</label>
                <input type="password" id="pass" name="pass" required>
            </div>
            <button type="submit" class="btn">Logga in</button>
            {% if error %}
                <div class="error">Fel användarnamn eller lösenord. Detta försök har loggats.</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

# 3. Route för att visa inloggningssidan
@app.route('/', methods=['GET'])
def index():
    return render_template_string(LOGIN_PAGE_HTML, error=False)

# 4. Route för att hantera själva inloggningsförsöket
@app.route('/login', methods=['POST'])
def login():
    # Fånga upp datan som skickas i formuläret
    username = request.form.get('user', '')
    password = request.form.get('pass', '')
    ip = request.remote_addr
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Spara datan till vår tabell (CSV)
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, username, password, "FAILED"])
    
    print(f"[LIVE HOT] Misslyckat inloggningsförsök! IP: {ip} | Användare: {username} | Lösenord: {password}")
    
    # Ladda om sidan och visa felmeddelandet
    return render_template_string(LOGIN_PAGE_HTML, error=True), 401

if __name__ == '__main__':
    print("Startar den falska inloggningsportalen...")
    print("Gå till http://127.0.0.1:5000 i din webbläsare!")
    app.run(port=5000, debug=True)