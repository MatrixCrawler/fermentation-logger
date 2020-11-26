#!venv/bin/python
import configparser
import os
import time
from datetime import datetime

import RPi.GPIO as GPIO
from influxdb import InfluxDBClient


def _write_measurement():
    global config
    influx = InfluxDBClient(config['Influx']['host'], int(config['Influx']['port']), config['Influx']['username'],
                        config['Influx']['password'],
                        config['Influx']['database'])
    data_point = dict(
        measurement=config['Influx']['measurement'],
        time=str(datetime.utcnow()),
        fields=dict(
            bubble=1
        )
    )
    influx.write_points([data_point])
    print("Event\n")
    influx.close()


def _setup_gpio():
    global config
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config['Sensor']['channel'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(config['Sensor']['channel'], GPIO.RISING, callback=_write_measurement, bouncetime=1000)


def main():
    _setup_gpio()
    try:
        while True:
            # warten!
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nI am out!")


"""main method"""
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.dirname(__file__) + "/config.ini")
    main()
