#!/usr/bin/env python

import configparser
import os
import time
from datetime import datetime

import adafruit_dht
import board
from influxdb import InfluxDBClient

options = {}


def _write_measurement():
    global config, dht_device
    humidity = dht_device.humidity
    temperature = dht_device.temperature
    influx = InfluxDBClient(config['Influx']['host'], int(config['Influx']['port']), config['Influx']['username'],
                            config['Influx']['password'],
                            config['Influx']['database'])
    data_point = dict(
        measurement=config['Influx']['measurement'],
        time=str(datetime.utcnow()),
        fields=dict(
            temperature=temperature,
            humidity=humidity
        )
    )
    influx.write_points([data_point])
    influx.close()


"""main method"""
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.dirname(__file__) + "/config.ini")
    dht_device = adafruit_dht.DHT22(board.D4)
    while True:
        try:
            # warten!
            _write_measurement()
            time.sleep(60)
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except KeyboardInterrupt:
            dht_device.exit()
            print("\nI am out!")
