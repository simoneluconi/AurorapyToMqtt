from aurorapy.client import AuroraError, AuroraTCPClient
import time
import paho.mqtt.client as mqtt
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("mqttUsername", "mqttPassword")
client.connect("mqttBroker", 1883, 60)
client.loop_start()

c = AuroraTCPClient(ip='192.168.2.9', port=8899, address=2)
c.connect()

while True:

    try:

        result = dict()
   
        #OUTPUT POWER
        output_power = c.measure(3)
        result["output_power"] = output_power
        print ("Power:" , output_power, "W")

        #INPUT 1 VOLTAGE
        input_voltage = c.measure(23)
        print ("Voltage:" , input_voltage, "V")
        result["input_voltage"] = input_voltage

        ampsTot = 0
        #INPUT 1 CURRENT
        input1_current = c.measure(25)
        print ("Amps1:" , input1_current, "A")
        ampsTot += input1_current

        #INPUT 2 CURRENT
        input2_current = c.measure(27)
        print ("Amps2:" , input2_current, "A")
        ampsTot += input2_current
        result["input2_current"] = input2_current

        #ENERGY DAILY
        daily_energy = c.cumulated_energy(period=0) / 1000
        print ("Energy Daily:" , daily_energy, "kWh")
        result["daily_energy"] = daily_energy

        #ENERGY WEEK
        energy_week = c.cumulated_energy(period=1) / 1000
        print ("Energy Weeek:" , energy_week, "kWh")
        result["energy_week"] = energy_week

        #ENERGY MONTH
        energy_month = c.cumulated_energy(period=3) / 1000
        print ("Energy Month:" , energy_month, "kWh")
        result["energy_month"] = energy_month

        #ENERGY YEAR
        year_energy = c.cumulated_energy(period=4) / 1000
        print ("Energy Year:" , year_energy, "kWh")
        result["year_energy"] = year_energy

        #ENERGY TOTAL
        energy_total = c.cumulated_energy(period=5) / 1000
        print ("Energy Total:" , energy_total, "kWh")
        result["energy_total"] = energy_total

        inverter_temperature = c.measure(21)
        print ("Inverter Tmperature:" , inverter_temperature, "°C")
        result["inverter_temperature"] = inverter_temperature

        jsonRes = json.dumps(result)
        client.publish("/solar/1", jsonRes)

    except Exception as e:
        print(e)

    print("-------------------------------------------------")
    time.sleep(2)


c.close()

