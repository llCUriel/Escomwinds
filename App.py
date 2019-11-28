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
import telnetlib
from netmiko import ConnectHandler
from mydevices import cisco_ios_centralrouter
from decimal import Decimal
import concurrent.futures
from datetime import date

centralRouterFilePath = "router/centralRouter"

app = Flask(__name__)

@app.route('/updateData')
def updateGraphData(methods = ['POST']):
    return "hola"

@app.route("/")
def index():
    today = date.today()
    print(today)
    return render_template('dashboard.html')

@app.route("/centralRouter")
def centralRouter():
    temperatureList, percentageList = [],[]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(obtainDataFromRouter, cisco_ios_centralrouter['ip'],"centralRouter")
        percentageList,temperatureList = future.result()

    return render_template('dashboard.html', temperatureList = temperatureList, percentageList = percentageList)

def obtainDataFromRouter(ip,hostname):
    temperatureList = [34,34,34,54,54,65]

    output = connectRouter(ip);
    percentageList  = obtainMemory(output)
    _temperatureList,cpuLoadList,timeUpList = obtainAllDataList(hostname)


    return percentageList, temperatureList

def obtainDataList(hostname):
    data = []
    definitiveRoute = choosePath(hostname)
    f = open(definitiveRoute,'r')
    for line in f:
        data.append(line.rstrip())
    f.close()
    for i in range(0,len(data)):
        data[i] = data[i].split('|')
    return data

def choosePath(hostname):
    if hostname == 'centralRouter':
        return centralRouterFilePath
    else:
        return ""


def obtainAllDataList(hostname):
    dataList = obtainDataList(hostname)
    temperatureList, cpuLoadList, timeUpList = [],[],[]
    dateIndex = 1

    for list in dataList:
        temperatureList.append([list[dateIndex],list[2]])
        cpuLoadList.append([list[dateIndex],list[4]])
        timeUpList.append([list[dateIndex],list[3]])

    return temperatureList,cpuLoadList,timeUpList

def connectRouter(ip):
    device = ConnectHandler(**cisco_ios_centralrouter)
    output = device.send_command("show process memory")
    return str(output)

def obtainMemory(routerOutput):
    x=routerOutput.split();
    unitValue = 100.0/int(x[3])
    freePercentage = Decimal(unitValue*int(x[5]))
    usedPercentage = Decimal(unitValue*int(x[7]))
    return [round(usedPercentage,2),round(freePercentage,2)]


def generateTemperature(min,max):
    return random.randrange(min,max)

if __name__ == "__main__":
    app.run(port=8001, debug=True)
