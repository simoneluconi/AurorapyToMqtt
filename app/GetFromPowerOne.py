from dotenv import load_dotenv
import os
from aurorapy.client import AuroraError, AuroraTCPClient

load_dotenv()

def PowerOne():

    try:

        c.connect()
        result = dict()

        product_number=c.pn()
        result["product_number"] = product_number

        serial_number=c.serial_number()
        result["serial_number"] = serial_number

        #OUTPUT POWER
        output_power = c.measure(3)
        result["output_power"] = output_power

        #INPUT 1 VOLTAGE
        input_voltage = c.measure(23)
        result["input_voltage"] = input_voltage

        ampsTot = 0
        #INPUT 1 CURRENT
        input1_current = c.measure(25)
        ampsTot += input1_current

        #INPUT 2 CURRENT
        input2_current = c.measure(27)
        ampsTot += input2_current
        result["input2_current"] = input2_current  

        #ENERGY DAILY
        daily_energy = c.cumulated_energy(period=0) / 1000
        result["daily_energy"] = daily_energy

        #ENERGY WEEK
        energy_week = c.cumulated_energy(period=1) / 1000
        result["energy_week"] = energy_week

        #ENERGY MONTH
        energy_month = c.cumulated_energy(period=3) / 1000
        result["energy_month"] = energy_month

        #ENERGY YEAR
        year_energy = c.cumulated_energy(period=4) / 1000
        result["year_energy"] = year_energy

        #ENERGY TOTAL
        energy_total = c.cumulated_energy(period=5) / 1000
        result["energy_total"] = energy_total

        inverter_temperature = c.measure(21)
        result["inverter_temperature"] = inverter_temperature

        return result

        c.close()

    except Exception as e:
        if str(e) == 'Unknown transmission state':
            print(e)
            result["output_power"] = 0.0
            time.sleep(60)
        else:
            print(e)