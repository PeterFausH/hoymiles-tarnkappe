# !/usr/bin/python
# -*- coding: utf-8 -*-
# Dank geht an https://github.com/tbnobody/OpenDTU
# Version 0.95    PFu 28.10.2022
# das Script ermittelt den aktuellen Bezug eines Stromzählers. Dazu wird der schon
# laufende Volkszähler abgefragt. Sonst den json vom Smartmeter nehmen etc.
# SunMan ist mein flexibles Modul mit 375Wp von SunMan
# die Seriennummer anpassen und die gewünschte zuweisen
# die apiURL mit dem Zugang zum Volkszähler muss angepasst werden
# maximum_wr muss angepasst werden auf max Wechselrichter oder Modulleistung


import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import requests
import json
import time
import sys

# Seriennummern der Hoymiles Wechselrichter
serial_SunMan = "112174217122"
serial_Trina = "112174217264"
maximum_wr = 400
# was kann das Modul / WR max abgeben

# hier die passende Seriennummer zuweisen
serial = serial_Trina
# mqtt-strings zum lesen und schreiben zusammensetzen
set_limit = "solar/"+serial+"/cmd/limit_nonpersistent_absolute"
akt_power = "solar/"+serial+"/0/power"  # aktuelle Lieferung ins Haus
akt_p_dc  = "solar/"+serial+"/0/powerdc"  # aktuelle Lieferung vom Panel
limit_alt = "solar/"+serial+"/status/limit_absolute" # das vorherige Limit


akt_reachable = "solar/"+serial+"/status/reachable"   
akt_producing = "solar/"+serial+"/status/producing" 

MQTT_TOPIC = [(akt_power,0),(akt_p_dc,0),(limit_alt,0)]

# Zugang zum Volkszähler MiniWeb
apiURL = "http://192.168.200.207:8080"  # miniweb des Volkszähler im Chalet
reachable = 1    # ist DTU erreichbar ?
producing = 1    # produziert der Wechselrichter etwas ?
grid_sum = 0     # aktueller Bezug im Chalet
setpoint = 0     # neues Limit in Watt
value = -1       # Rückgabewert
altes_limit = 0  # wo war das alte Limit gesetzt
power = 0        # Abgabe BKW AC in Watt
power_dc = 0     # Lieferung DC vom Panel
got_power = False
got_power_dc = False
# paho_mqtt läuft lokal
server = "localhost"
port = 1883

# Configure InfluxDB connection variables
influx_host = "localhost" 
# influx_host = "192.168.22.210"
influx_port = 8086 
user = "hoy"
password = "miles"
dbname = "dtu" 

# Influx Datenbank verbinden
influx_client = InfluxDBClient(influx_host, influx_port, user, password, dbname)


# json zusammenbauen für Influx-Datenbank
def add(name,wert):
    info=[{"measurement": "opendtu",
           "fields": {name : wert}}]
    print(info)
    influx_client.write_points(info, time_precision='m')
    return

# es wurde eine allgemeine mqtt Nachricht empfangen
def on_message(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    print("on_message",message_received)

# es wurde eine bestimmte mqtt Nachricht empfangen
def on_message_reachable(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global reachable
    reachable = int(float(message_received))
    if reachable: print("DTU ist erreichbar!")
    else:
        print("Problem: DTU ist NICHT erreichbar!")
        client.disconnect()

def on_message_producing(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global producing
    producing = int(float(message_received))
    if producing: print("Wechselrichter arbeitet!")
    else:
        client.disconnect()

def on_message_power(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global power
    power = int(float(message_received))
    if reachable: print("BKW liefert aktuell :    ", power)
    global got_power
    got_power = True
    if (got_power & got_power_dc):
        client.disconnect()

def on_message_power_dc(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global power_dc
    power_dc = int(float(message_received))
    if reachable: print("Panel liefert aktuell :  ", power_dc)
    global got_power_dc
    got_power_dc = True
    if (got_power & got_power_dc):
        client.disconnect()


def on_message_altes_limit(client, userdata, message):
    message_received = str(message.payload.decode("utf-8"))
    global altes_limit
    altes_limit = int(float(message_received))
    if reachable:
        print("altes_limit war bei   :  ", altes_limit)
        if altes_limit >= maximum_wr:
            altes_limit = maximum_wr
            print(" altes Limit korrigiert auf ", maximum_wr)


# zum mqtt Broker verbunden
def on_connect(client, userdata, flags, rc):
    #print(got_power,got_power_dc)
    if rc==0:
        client.connected_flag=True #set flag
        print("MQTT erreichbar, connect ok")
        time.sleep(1)
    else:
        print("MQTT, Bad connection Returned code=",rc)

def on_disconnect(client, userdata, rc):
    print("MQTT: disconnected!")


# Bezug vom Chalet feststellen
r = requests.get(apiURL)  # Volkszähler lesen
json_string = r.text
parsed_json = json.loads(json_string)
# hier anpassen an json Ausgabe
grid_sum = int(parsed_json['data'][1]['tuples'][0][1])
print(grid_sum)
# Strombezug ist jetzt bekannt
# ------------------------------------- Ende Chalet Bezug feststellen

# zum mqtt server verbinden
mqtt.Client.connected_flag=False  #create flag in class
client = mqtt.Client("DTU")
client.connect(server,port)
#print("Skript: Statusabfragen laufen")
# auf bestimmte Messages reagieren
client.message_callback_add(akt_reachable, on_message_reachable)
client.message_callback_add(akt_power, on_message_power)
client.message_callback_add(akt_producing, on_message_producing)
client.message_callback_add(akt_p_dc, on_message_power_dc)
client.message_callback_add(limit_alt, on_message_altes_limit)

client.on_message = on_message
client.subscribe('solar/'+serial+'/#')
client.on_connect = on_connect
client.loop_forever()
#--------------------- Ende erster Teil: Datenermittlung


# Werte setzen
client = mqtt.Client("DTU-2")
client.connect(server,port)
# print("Skript: Limit setzen läuft")
client.loop_start()
client.subscribe(set_limit)
print("aktueller Bezug Chalet:   ",grid_sum)
# print("Skript: Limiter korrigieren läuft")
# limiter korrigieren falls er maximum_wr übersteigt,
# falls mehr Strom bezogen wird als der Wechselrichter liefern könnte,
# oder falls nichts vom Wechselrichter kommt.
# oder wenn das Limit unter 100 Watt wäre (Versuchsweise)
if reachable:
    if (altes_limit >= maximum_wr or grid_sum >= maximum_wr or setpoint >= maximum_wr):
        print("setze Limiter auf maximum_wr")
        setpoint = maximum_wr
    # wir weniger bezogen als maximum_wr dann neues Limit ausrechnen
    if (grid_sum+altes_limit) <= maximum_wr:
        setpoint = grid_sum + altes_limit -5
        print("setpoint:",grid_sum,"+",altes_limit,"-5 ")
        print("neues Limit berechnet auf ",setpoint)
    if setpoint <= 100:
        setpoint = 100
        print("setpoint: 100 minimum gesetzt")
        print("neues Limit festgelegt auf ",setpoint)
        
    print("setze Einspeiselimit auf: ",setpoint)
    # neues limit setzen
    client.publish(set_limit,setpoint)
    print("Panel-power:",power,"  Setpoint:",setpoint)
    time.sleep(2) # wait
# neues Limit mit 0 macht keinen Sinn, irgend ein Fehler..
if setpoint == 0: setpoint = grid_sum
if not reachable: setpoint = maximum_wr
client.loop_stop() #stop loop 
client.disconnect() # disconnect

# Ausgabe an die Influx-Datenbank
if reachable == True:
    add('altes_limit',altes_limit)
else:
    add('altes_limit',setpoint)
add('reachable',int(reachable))
add('producing',int(producing))
add('akt_p_dc',int(power_dc))
add('akt_power',int(power))
add('grid_sum',int(grid_sum))
add('setpoint',int(setpoint))

# Ende Skript
