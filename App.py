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
import datetime
from datetime import date
import time

centralRouterFilePath = "router/centralRouter"
connectionList = []
ipList = ["10.200.200.22"]
app = Flask(__name__)


def connectAllDevices():
    for ip in ipList:
        connectionList.append(connectRouter(ip))


def generateRandomNumber(min,max):
    return random.randint(min,max)

@app.route('/updateData')
def updateGraphData(methods = ['POST']):
    return "hola"

@app.route("/")
def index():
    connectAllDevices()
    return render_template('dashboard.html')


def obtainLastIndex(someList):
    listLenght = len(someList)

    if listLenght > 0:
        return someList[len(someList)-1][0]
    else:
        return 0


def obtainCPULoad(output):
    firstLine = output.splitlines()[0]
    listFirstLine = firstLine.split()
    cpuLoad =(((listFirstLine[5].split('/'))[0]).split('%'))[0]
    return cpuLoad


def obtainUpAndDownInterfaces(output):
    downInterfaces, upInterfaces, interfaces = [],[],[]
    filterInterfacesLine = output.splitlines()
    for item in filterInterfacesLine:
        if 'line protocol' in item:
            interfaces.append(item)
    for item in interfaces:
        finalStr = item.split(' ')[0]
        if 'up' in item:
            upInterfaces.append(finalStr)
        if 'down' in item:
            downInterfaces.append(finalStr)
    return downInterfaces, upInterfaces


def obtainDeviceNeighbors(output):
    finalList = []
    splitLines = output.splitlines()[4:]
    for item in splitLines:
        finalList.append(item.split()[:-6])


    return finalList

def obtainDataFromRouter(ip,hostname):

    device = connectionList[0]
    output1 = device.send_command("show process memory")
    output2 = device.send_command("sh version")
    output3 = device.send_command("sh processes cpu sorted")
    output4 = device.send_command("sh ip traffic")
    output5 = device.send_command("sh interfaces")
    output6 = device.send_command("sh cdp neighbors")
    deviceneighbors = obtainDeviceNeighbors(output6)
    downInterfaces, upInterfaces = obtainUpAndDownInterfaces(output5)
    inTraffic  = obtainTrafficin(output4)
    outTraffic = obtainTrafficout(output4)

     #ip ,icmp,tcp,bgp,ip-eigrp,udp,ospf,arp

    NVRAM, _memory = obtainNVRAMAndMemory(output2)
    _hostname = obtainHostName(output2)
    percentageList, freeSpace,usedSpace  = obtainMemory(output1)
    timeUp = obtainTimeUp(output2)
    cpuLoad = obtainCPULoad(output3)
    #availableBandWidth = obtainAvilableBandWidth()
    #EscribirRegistro(hostname,'1',str(date.today()),"34.6",timeUp,"100");
    #temperatura = obtainTemperatura(output3)
    #carga = obtainCarga(output4)
    #EscribirRegistro(hostname,1,date.today(),temperatura,timeUp,obtainCarga);
    temperatureList,cpuLoadList,timeUpList = obtainAllDataList(hostname)
    lastIndex = int(obtainLastIndex(timeUpList))
    newTemperature = str(generateRandomNumber(39,45))
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    writeRegister(hostname,lastIndex+1,current_time,newTemperature,timeUp,cpuLoad)
    timeUpList.append([lastIndex+1,current_time,timeUp])
    temperatureList.append([lastIndex+1,current_time,newTemperature])
    cpuLoadList.append([lastIndex+1,current_time, cpuLoad])
    freeSpace = str(freeSpace)
    usedSpace = str(usedSpace)

    return percentageList, temperatureList,timeUpList,cpuLoadList, freeSpace, usedSpace, timeUp, newTemperature, downInterfaces, upInterfaces, deviceneighbors, NVRAM, _memory, _hostname,inTraffic,outTraffic

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
        cpuLoadList.append([list[0],list[dateIndex],int(list[4])])
        timeUpList.append([list[0],list[dateIndex],int(list[3])])
    return temperatureList,cpuLoadList,timeUpList

def connectRouter(ip):
    if ip == ipList[0]:
        return ConnectHandler(**cisco_ios_centralrouter)
    return False

def obtainMemory(routerOutput):
    x=routerOutput.split();
    unitValue = 100.0/int(x[3])
    freeSpace = int(x[5])
    usedSpace = int(x[7])
    freePercentage = Decimal(unitValue*freeSpace)
    usedPercentage = Decimal(unitValue*usedSpace)
    return [round(usedPercentage,2),round(freePercentage,2)], freeSpace, usedSpace


def generateTemperature(min,max):
    return random.randrange(min,max)

def obtainTrafficin(output):
    F=output.split();
    data=[int(F[3]),int(F[143]),int(F[219]),int(F[233]),int(F[263]),int(F[335]),int(F[352]),int(F[397])]

     #ip ,icmp,tcp,bgp,ip-eigrp,udp,ospf,arp
    return data

def obtainTrafficout(output):
    F=output.split();
    data=[int(F[95]),int(F[182]),int(F[228]),int(F[248]),int(F[266]),int(F[344]),int(F[375]),int(F[406])]
     #ip ,icmp,tcp,bgp,ip-eigrp,udp,ospf,arp
    return data

def obtainNVRAMAndMemory(output):
    splitLines = output.splitlines()
    NVRAMLine = ""
    memoryLine = ""
    for item in splitLines:
        if 'NVRAM' in item:
            NVRAMLine = item
        if 'bytes of memory' in item:
            memoryLine = item

    NVRAMLine = NVRAMLine.split()[0]
    memoryLine = memoryLine.split()[7]

    return NVRAMLine, memoryLine


def obtainHostName(output):
    splitLines = output.splitlines()
    str = ""
    for item in splitLines:
        if 'uptime' in item:
            str = item
    return str.split()[0]

@app.route("/R1")
def R1():
    return "R1"
@app.route("/R2")
def R2():
    return "R2"
@app.route("/R3")
def R3():
    return "R3"
@app.route("/R4")
def R4():
    return "R4"
@app.route("/R5")
def R5():
    return "R5"
@app.route("/R6")
def R6():
    deviceName = "C3745-ADVENTERPRISEK9-M"
    deviceVersion = "Version 12.4(25d)"
    technicalSupport = "http://www.cisco.com/techsupport"
    processorBoardID = "FTX0945W0MY"
    ipAddress = ipList[0]
    temperatureList, percentageList, timeUpList, cpuLoadList = [],[],[],[]

    #EscribirRegistro("centralRouter","2","2019-11-27","50","100","21\n")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(obtainDataFromRouter, cisco_ios_centralrouter['ip'],"centralRouter")
        percentageList,temperatureList,timeUpList, cpuLoadList, freeSpace,usedSpace, lastTimeUp, lastTemperature, downInterfaces, upInterfaces, deviceneighbors, NVRAM,_memory, _hostname,inTraffic,outTraffic = future.result()

    temperatureList = temperatureList[-5:]
    timeUpList = (timeUpList[-5:])[::-1]
    cpuLoadList = cpuLoadList[-5:]

    return render_template('dashboard.html', temperatureList = temperatureList,
                                              percentageList = percentageList,
                                              timeUpList = timeUpList,
                                              cpuLoadList = cpuLoadList,
                                              deviceName = deviceName,
                                              deviceVersion = deviceVersion,
                                              freeSpace = freeSpace, usedSpace = usedSpace,
                                              technicalSupport = technicalSupport,
                                              lastTimeUp = lastTimeUp, lastTemperature = lastTemperature,
                                              processorBoardID = processorBoardID,
                                              downInterfaces = downInterfaces,
                                              upInterfaces = upInterfaces,
                                              ipAddress = ipAddress,
                                              deviceneighbors = deviceneighbors,
                                              totalSpace = usedSpace+freeSpace,
                                              NVRAM = NVRAM,
                                              _memory = _memory,
                                              _hostname = _hostname,
                                              inTraffic = inTraffic,
                                              outTraffic = outTraffic)


if __name__ == "__main__":
    app.run(port=8001, debug=True)
