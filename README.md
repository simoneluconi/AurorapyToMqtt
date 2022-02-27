# AurorapyToMqtt
_Forked from simoneluconi/AurorapyToMqtt_

Docker container to send data from serial or TCP communication from Aurora Inverters (ABB) to MQTT

# How to use
Run the docker container with the provided docker-compose.yml
Don't forget to adapt it to your needs :smile:

# Example of the json payload
```
{
    "product_number": "-12M8-",
    "serial_number": "123456",
    "output_power": 0.0,
    "input_voltage": 0.0,
    "input1_current": 0.0,
    "input2_current": 0.0,
    "ampsTot": 0.0,
    "inverter_temperature": 0.0,
    "daily_energy": 0.0,
    "energy_week": 0.0,
    "energy_month": 0.0,
    "year_energy": 0.0,
    "energy_total": 0.0
}
```

# Future developpement
- [ ] Auto discovery by Home-Assistant
- [ ] Improve python coding style as I'm only a (very) part time developper :laugh: