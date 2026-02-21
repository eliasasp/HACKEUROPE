import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

def animate(i):
    try:
        with open("attack_log.txt", "r") as f:
            lines = f.readlines()
        
        # Vi räknar hur många attacker som skett per sekund
        timestamps = []
        for line in lines:
            # Extrahera tidstämpeln [YYYY-MM-DD HH:MM:SS]
            ts_str = line.split(']')[0].strip('[')
            ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            timestamps.append(ts)

        # Gruppera data (antal attacker per tidsenhet)
        if timestamps:
            plt.cla() # Rensa grafen
            plt.hist(timestamps, bins=20, color='red', alpha=0.7)
            plt.gcf().autofmt_xdate()
            plt.title("Realtidsvisualisering av Poisson-attacker")
            plt.ylabel("Antal försök")
            plt.xlabel("Tid")
    except Exception as e:
        pass

fig = plt.figure()
ani = animation.FuncAnimation(fig, animate, interval=1000) # Uppdatera varje sekund
plt.show()