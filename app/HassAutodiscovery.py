import json

def Advertise (client, PowerOne, topic):
    print(PowerOne)

    DeviceBase = {
        "availability": {
            "topic": topic+"/status"
        },
        "device": {
            "name": "Solaire PowerOne",
            "identifiers": PowerOne["serial_number"],
            "model": PowerOne["serial_number"]
        }
    }

    Payload = {
        "name": "Puissance instantannée solaire",
        "unique_id": "sensor.puissance_instantannee_solaire",
        "state_topic": topic,
        "unit_of_measurement": "W",
        "value_template": "{{ value_json.output_power | round(1)}}",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:solar-power"
    }

    Payload = Payload | DeviceBase

    client.publish("homeassistantTest/sensor/"+PowerOne["serial_number"]+"/"+Payload["unique_id"]+"/config",payload=json.dumps(Payload), qos=0, retain=True)

    Payload = {
        "name": "Solar Panel Total Production",
        "unique_id": "sensor.solar_panel_total_production",
        "state_topic": "solar/1",
        "unit_of_measurement": "kWh",
        "value_template": "{{ value_json.energy_total | round(1)}}",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:solar-power-variant"
    }

    Payload = Payload | DeviceBase

    client.publish("homeassistantTest/sensor/"+PowerOne["serial_number"]+"/"+Payload["unique_id"]+"/config",payload=json.dumps(Payload), qos=0, retain=True)


    return