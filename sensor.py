#!/usr/bin/env python

import time
from datetime import datetime

import RPi.GPIO as GPIO
from influxdb import InfluxDBClient

GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

bubble_counter = 0


def my_callback(channel):
    global bubble_counter
    bubble_counter += 1
    print(str(channel) + ", Bubbles: " + str(bubble_counter))
    args = dict(username="USER", password="PASSWORD", host="localhost",
                database="DBName")
    influx = InfluxDBClient(**args)
    data_point = dict(
        measurement="measurement",
        time=str(datetime.utcnow()),
        fields=dict(
            bubble=1
        )
    )
    influx.write_points([data_point])
    influx.close()


GPIO.add_event_detect(14, GPIO.RISING, callback=my_callback, bouncetime=1000)
try:
    while True:
        # warten!
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nI am out!")
