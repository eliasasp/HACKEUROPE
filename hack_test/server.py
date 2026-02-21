from flask import Flask, request, render_template_string
import datetime

app = Flask(__name__)

# En enkel HTML-sida med ett inloggningsformulär
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Säker Portal</title></head>
<body>
    <h2>Logga in</h2>
    <form method="POST" action="/login">
        Användarnamn: <input type="text" name="user"><br>
        Lösenord: <input type="password" name="pass"><br>
        <input type="submit" value="Logga in">
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('user')
    ip = request.remote_addr
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Logga attackförsöket till en fil
    with open("attack_log.txt", "a") as f:
        f.write(f"[{timestamp}] Inloggningsförsök från {ip} - Användare: {username}\n")
    
    print(f"!!! INLOGGNINGSFÖRSÖK UPPTÄCKT: {username} !!!")
    return "Inloggning misslyckades", 401

if __name__ == '__main__':
    # Starta servern lokalt
    app.run(port=5000)