# AurorapyToMqtt
Library to send data from serial or TCP communication from Aurora Inverters (ABB) to MQTT

# How to use
Download the AuroraComm.py file, replace the parameters for your mqtt broker and communcation adapter, install the dependencies and run it :)

# Home Assistant
Even though home assistant has its own library to communicate with the inverter, in my opinion it is not very well implemented. You can only use serial communication and the only data returned are actual power, total energy produced and temperature. I was not even able to implement the data in the new energy dashboard. I tried to look at the library but i really don't know where to start to implement these changes. So for now i provide the template to read the data from mqtt.

```
mqtt:
  sensor:
      - name: "Solar Panel Power"
        state_topic: "/solar/1"
        unit_of_measurement: "W"
        value_template: "{{ value_json.output_power | round(1)}}"
        device_class: "power"
        state_class: "measurement"
      - name: "Solar Panel Voltage"
        state_topic: "/solar/1"
        unit_of_measurement: "V"
        value_template: "{{ value_json.input_voltage | round(1)}}"
        device_class: "voltage"
        state_class: "measurement"
      - name: "Solar Panel Current"
        state_topic: "/solar/1"
        unit_of_measurement: "A"
        value_template: "{{ value_json.input2_current | round(1)}}"
        device_class: "current"
        state_class: "measurement"
        name: "Solar Panel Daily Production"
        state_topic: "/solar/1"
        unit_of_measurement: "kWh"
        value_template: "{{ value_json.daily_energy | round(1)}}"
        device_class: "energy"
        state_class: "total"
      - name: "Solar Panel Weekly Production"
        state_topic: "/solar/1"
        unit_of_measurement: "kWh"
        value_template: "{{ value_json.energy_week | round(1)}}"
        device_class: "energy"
        state_class: "total"
      - name: "Solar Panel Montly Production"
        state_topic: "/solar/1"
        unit_of_measurement: "kWh"
        value_template: "{{ value_json.energy_month | round(1)}}"
        device_class: "energy"
        state_class: "total"
      - name: "Solar Panel Annual Production"
        state_topic: "/solar/1"
        unit_of_measurement: "kWh"
        value_template: "{{ value_json.year_energy | round(1)}}"
        device_class: "energy"
        state_class: "total"
      - name: "Solar Panel Total Production"
        state_topic: "/solar/1"
        unit_of_measurement: "kWh"
        value_template: "{{ value_json.energy_total | round(1)}}"
        device_class: "energy"
        state_class: "total_increasing"
      - name: "Solar Panel Temperature"
        state_topic: "/solar/1"
        unit_of_measurement: "°C"
        value_template: "{{ value_json.inverter_temperature | round(1)}}"
```
