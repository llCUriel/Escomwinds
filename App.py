from flask import Flask
from flask import render_template
from netmiko import ConnectHandler
import subprocess
import threading
import random
import time
from flask import redirect
from flask import url_for
import json
from flask import Response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('dashboard.html')

@app.route("/routerCentral")
def routerCentral():
    listaDeTemperaturas = generarTemperatura(40,100)
    return render_template('dashboard.html', listaDeTemperaturas = listaDeTemperaturas)

def conectarARouter(ip):
    command = "telnet 10.168.100.22"
    subprocess.call(command, shell=True)


def generarTemperatura(min,max):
    listaDeTemperaturas = []
    temperature = random.randrange(min,max)
    listaDeTemperaturas.append(temperature)
    return listaDeTemperaturas

if __name__ == "__main__":
    app.run(port=8001, debug=True)
