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


@app.route('/updateData')
def updateGraphData(methods = ['POST']):

    return "hola"

@app.route("/")
def index():
    return render_template('dashboard.html')

@app.route("/routerCentral")
def routerCentral():
    listaDeTemperaturas = [20,34,34,34,34]
    conectarARouter("sadsa");
    listaDePorcentajes,espacioUsado, espacioDisponible  = obtener_Memoria()
    return render_template('dashboard.html', listaDeTemperaturas = listaDeTemperaturas,listaDePorcentajes=listaDePorcentajes, espacioUsado=espacioUsado, espacioDisponible=espacioDisponible)

def conectarARouter(ip):
    command = "telnet "+ip
    subprocess.call('ls', shell=True)


def obtener_Memoria():
    #command="show process memory"
    #Salida=subprocess.check_output(command, shell=True)
    salidaDeLaTerminal="Chido uno Total: 10 Used: 5 Free: 6"
    x=salidaDeLaTerminal.split();
    valorUnitario = 100.0/int(x[3])
    porcentajeUsado = valorUnitario*int(x[5])
    porcentajeLibre = valorUnitario*int(x[7])
    return [porcentajeUsado,porcentajeLibre], int(x[5]), int(x[7])


def generarTemperatura(min,max):
    listaDeTemperaturas = []
    temperature = random.randrange(min,max)
    listaDeTemperaturas.append(temperature)
    return listaDeTemperaturas

if __name__ == "__main__":
    app.run(port=8001, debug=True)
