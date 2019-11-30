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
    temperatureList, percentageList, timeUpList = [],[],[]

    #EscribirRegistro("centralRouter","2","2019-11-27","50","100","21\n")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(obtainDataFromRouter, cisco_ios_centralrouter['ip'],"centralRouter")
        percentageList,temperatureList,timeUpList = future.result()


    temperatureList = temperatureList[-7:]

    return render_template('dashboard.html', temperatureList = temperatureList, percentageList = percentageList)


def obtainLastIndex(someList):
    return someList[len(someList)-1][0]


def obtainDataFromRouter(ip,hostname):
    device = connectRouter(ip);

    output1 = device.send_command("show process memory")
    output2 = device.send_command("sh version")

    percentageList  = obtainMemory(output1)
    timeUp = obtainTimeUp(output2)

    #EscribirRegistro(hostname,'1',str(date.today()),"34.6",timeUp,"100");

    #temperatura = obtainTemperatura(output3)
    #carga = obtainCarga(output4)
    #EscribirRegistro(hostname,1,date.today(),temperatura,timeUp,obtainCarga);
    temperatureList,cpuLoadList,timeUpList = obtainAllDataList(hostname)
    lastIndex = int(obtainLastIndex(timeUpList))
    writeRegister(hostname,lastIndex+1,date.today(),'23',timeUp,'23')



    return percentageList, temperatureList,timeUp

def obtainTemperatura(output):
    print(output)

def obtainCarga(output):
    print(output)

def obtainTimeUp(output):
    return output.split()[43]


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



def writeRegister(hostname,id,date,temperature,timeup,cpuload):
    definitiveRoute = choosePath(hostname)
    f = open(definitiveRoute,'a')
    line = str(id)+'|'+str(date)+'|'+temperature+'|'+timeup+'|'+cpuload+'\n'
    f.write(line)
    f.close()

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
        temperatureList.append([list[0],list[dateIndex],list[2]])
        cpuLoadList.append([list[0],list[dateIndex],list[4]])
        timeUpList.append([list[0],list[dateIndex],list[3]])
    return temperatureList,cpuLoadList,timeUpList

def connectRouter(ip):
    return ConnectHandler(**cisco_ios_centralrouter)

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
