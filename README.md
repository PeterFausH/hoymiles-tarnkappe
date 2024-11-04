## hoymiles-tarnkappe

## Description
ein python-skript liest aus dem Volkszähler den aktuellen Hausverbrauch an Strom ab. In Abhängigkeit dessen wird ein Hoymiles Mikrowechselrichter in der Leistungsabgabe limitiert. Dazu wird das Projekt openDTU verwendet. Statt Volkszähler kann das alternativ ein USB-Lesekopf für SML-Protokoll, ein Smartmeter von Fronius oder der Shelly3EM sein.


## Visuals
a dashboard example using influxDB and Grafana
![dashboard](/media/hoymiles_tarnkappe_dashboard.png "using Grafana dashboard")
the used hardware
![hardware](/media/hoymiles_tarnkappe_komponenten.jpg "used hardware panel, hoymiles, esp32")
first success python talks to openDTU
![openDTU](/media/hoymiles_tarnkappe_limiter_in_openDTU.png "MQTT sent to openDTU limits hoymiles")
paho-mqtt used to talk to openDTU
![python](/media/hoymiles_tarnkappe_limiter_python_openDTU.png "first success python to openDTU")
nearly no energy needed from grid
![compensation](/media/hoymiles_tarnkappe_null-Linie.png "nearly perfect compensated electric consumption")
same period as above shown in Volkszaehler
![Volkszaehler](/media/hoymiles_tarnkappe_Volkszähler_gesamt.png "same period shown in Volkszaehler")
compensated energy for the additional small studio
![Gartenstudio](/media/hoymiles_tarnkappe_Ferienwohnung_Gartenstudio.png "same period with electric consumption in the studio")
compensated energy for the pellet stove
![Pelletheizung](/media/hoymiles_tarnkappe_Pelletheizung.png "all energy use by pellet stove compensated")
succesfull compensated all energy needed to produce multiple kWh solar thermal energy
![Solarthermie](/media/hoymiles_Tarnkappe_Solarthermie.png "nearly no electrical consumption but gained solar energy by solarthermie")


## Installation
Zuerst installiert ihr euch openDTU auf einem esp32 mit dem RF Modul. 
Danach habe ich einen RaspberryPi genommen, den MQTT-Broker Mosquitto installiert und ihn in openDTU angegeben.
Für Python installiert ihr euch den paho-mqtt-client und requests um auf Volkszähler oder andere Geräte zugreifen zu können. 
Optional installiert ihr den InfluxDBClient um die Daten an eine Influx-Datenbank weiterzugeben und mit Grafana ein Dashboard visualisieren zu können. 
Das Python-Skript ruft ihr dann in der Crontab jede Minute auf.

## Usage
Im python-Skript tragt ihr die Seriennummern des Hoymiles Wechselrichters ein und das Maximum vom Wechselrichter oder vom Modul, je nachdem, was kleiner ist.
Passt die URL vom Volkszähler an oder schreibt euch eine eigene Abfrage um an den aktuellen Stromverbrauch zu kommen. Nach dem Eintrag in der Crontab setzt das Python-Skript den Limit des Hoymiles auf den aktuellen Stromverbrauch abzüglich 5 Watt.
- Abfrage aktueller Stromverbrauch
- was liefert das Balkonkraftwerk aktuell AC-seitig ?
- wie war das alte Limit gesetzt ?
- Differenz berechnen Strombezug minus altes Limit
- neues Limit setzen auf altes Limit plus Delta minus 5, es sei denn, der Hausverbrauch ist höher als maximum_wr, dann limit auf Maximum setzen.
- Ausgabe aller Werte in eine Influx-Datenbank
Ende des Skripts.

## Support
for all your questions use pf@nc-x.com

## Roadmap
may be i try to have more action than 1 per minute

## Contributing
this was my first experience with mqtt and python. I tried a lot and it would be great if someone could improve that part.

## Authors and acknowledgment
based on https://github.com/tbnobody/OpenDTU which is the wonderful result from a community

## License
MIT Lizenz.

## Project status
ongoing
