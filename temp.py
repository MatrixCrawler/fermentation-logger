#!/usr/bin/env python

import argparse
import time
from datetime import datetime

import Adafruit_DHT as dht
from influxdb import InfluxDBClient

options = {}


def _write_measurement():
    global options
    (humi, temp) = dht.read_retry(dht.DHT22, options.channel)
    args = dict(username=options.influx_username, password=options.influx_password, host=options.influx_hostname,
                database=options.influx_database)
    influx = InfluxDBClient(**args)
    data_point = dict(
        measurement=options.influx_measurement,
        time=str(datetime.utcnow()),
        fields=dict(
            temperature=temp,
            humidity=humi
        )
    )
    influx.write_points([data_point])
    influx.close()


def _read_parser():
    global options
    parser = argparse.ArgumentParser(conflict_handler="resolve",
                                     description="This will track a DHT22 Sensor on specific channel and post events in InfluxDB")
    parser.add_argument("-H", "--host", type=str, dest="influx_hostname", help="The hostname of the InfluxDB",
                        default="localhost")
    parser.add_argument("-U", "--username", type=str, dest="influx_username", help="The username for the InfluxDB",
                        required=True)
    parser.add_argument("-P", "--password", type=str, dest="influx_password", help="The password for the InfluxDB",
                        required=True)
    parser.add_argument("-D", "--database", type=str, dest="influx_database", help="The database in theInfluxDB",
                        required=True)
    parser.add_argument("-M", "--measurement", type=str, dest="influx_measurement",
                        help="The measurement in theInfluxDB Database", required=True)
    parser.add_argument("-C", "--channel", type=int, dest="channel",
                        help="The channel on the GPIO Board", required=True)
    options = parser.parse_args()
    if not options.influx_username:
        parser.error("Username not given")
    if not options.influx_password:
        parser.error("Password not given")
    if not options.influx_database:
        parser.error("Database not given")
    if not options.influx_measurement:
        parser.error("Measurement not given")
    if not options.channel:
        parser.error("Channel not given")


def main():
    global options
    _read_parser()
    try:
        while True:
            # warten!
            _write_measurement()
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nI am out!")


"""main method"""
if __name__ == "__main__":
    main()
