#!venv/bin/python
import configparser
import logging
import os
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import RPi.GPIO as GPIO
import adafruit_dht
import board
from influxdb import InfluxDBClient


def _cache_measurement(channel):
    global config, data_points, last_send, dht_device
    # humidity = dht_device.humidity
    # temperature = dht_device.temperature
    data_point = dict(measurement=config['Influx']['measurement'], time=str(datetime.utcnow()),
                      fields=dict(bubble=1))
    data_points.append(data_point)
    logger.info("Appended datapoint: " + str(data_point))
    _send_data()


def _send_data():
    """
    Check if data needs to be stored into the influxdb.
    Will send every ten minutes if there was an event
    """
    global config, last_send, data_points
    now = datetime.utcnow()
    if (now - last_send).total_seconds() >= (60 * 10):
        influx = InfluxDBClient(config['Influx']['host'], int(config['Influx']['port']), config['Influx']['username'],
                                config['Influx']['password'],
                                config['Influx']['database'])
        # influx.write_points(data_points)
        influx.close()
        logger.info("Sent " + str(len(data_points)) + " points to Influxdb")
        last_send = now
        data_points = []


def _setup_gpio():
    global config
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(config['Sensor']['channel']), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(int(config['Sensor']['channel']), GPIO.RISING, callback=_cache_measurement, bouncetime=1000)


def main():
    logger.info("Starting Bubblecounter")
    _setup_gpio()
    try:
        while True:
            # warten!
            time.sleep(1)
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nI am out!")
        exit(0)


"""main method"""
if __name__ == "__main__":
    # Setup logging
    if not os.path.isdir("log"):
        os.makedirs("log")
    logger = logging.getLogger(os.path.basename(__file__))
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(os.path.dirname(__file__) + '/log/bubblecounter.log', when="d", interval=1,
                                       backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    data_points = []
    last_send = datetime.utcnow()
    config = configparser.ConfigParser()
    config.read(os.path.dirname(__file__) + "/config.ini")
    dht_device = adafruit_dht.DHT22(board.D7, use_pulseio=False)
    main()
