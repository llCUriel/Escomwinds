from flask import Flask
from flask import render_template
from netmiko import ConnectHandler
import subprocess
import threading


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('dashboard.html')

@app.route("/routerCentral")
def routerCentral():
    t = threading.Thread(target=conectarARouter, args=('10.168.100.22',))
    t.start()
    return render_template('dashboard.html')

def conectarARouter(ip):
    command = "telnet 10.168.100.22"
    subprocess.call(command, shell=True)


if __name__ == "__main__":
    app.run(port=8001, debug=True)
