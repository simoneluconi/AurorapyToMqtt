import json

def Advertise (client, PowerOne, topic):

    DeviceBase = {
        "availability": {
            "topic": topic+"/status"
        },
        "device": {
            "name": "Solaire PowerOne",
            "identifiers": PowerOne["serial_number"],
            "model": PowerOne["product_number"],
            "manufacturer": "ABB PowerOne"
        }
    }

    Payload = {
        "name": "Puissance instantannée",
        "unique_id": "puissance_instantannee",
        "state_topic": topic,
        "unit_of_measurement": "W",
        "value_template": "{{ value_json.output_power | round(1)}}",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:solar-power"
    }

    Payload = Payload | DeviceBase

    client.publish("homeassistant/sensor/"+PowerOne["serial_number"]+"/"+Payload["unique_id"]+"/config",payload=json.dumps(Payload), qos=0, retain=True)

    Payload = {
        "name": "Total Production",
        "unique_id": "total_production",
        "state_topic": "solar/1",
        "unit_of_measurement": "kWh",
        "value_template": "{{ value_json.energy_total | round(1)}}",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:solar-power-variant"
    }

    Payload = Payload | DeviceBase

    client.publish("homeassistant/sensor/"+PowerOne["serial_number"]+"/"+Payload["unique_id"]+"/config",payload=json.dumps(Payload), qos=0, retain=True)
