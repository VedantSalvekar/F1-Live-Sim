import asyncio
from functools import partial
import json
import time
import types
import logging

import typer
from dataimporter.message_handler import messageHandler
from fastf1.utils import to_datetime
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from fastf1.livetiming.client import SignalRClient

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

token = "LoOFvHw1tUXrUZ8oUqaozmEjxxG9UNO5H5YfRI4cGu306xwQVu_KMNxRYRMrWbhdD886N2PuRgpo9v4v_58pHw=="
org = "f1"
bucket = "data"

app = typer.Typer()


def sanitizeJsonData(line):
    line = line.replace("'", '"') \
        .replace('True', 'true') \
        .replace('False', 'false')
    return line


def writeToFile(writeAPI, self, msg):
    msg = sanitizeJsonData(msg)
    try:
        cat, msg, dt = json.loads(msg)
    except (json.JSONDecodeError, ValueError):
        log.warning("Json parse error")
        return

    try:
        dt = to_datetime(dt)
    except (ValueError, TypeError):
        log.warning("Datetime parse error {}", dt)
        return

    points = messageHandler(cat, msg, dt)
    for point in points:
        writeAPI.write(bucket, org, point)


def initiateWrite(self):
    """Connect to the data stream and start writing the data."""
    try:
        asyncio.run(self._async_start())
    except KeyboardInterrupt:
        self.logger.warning("Keyboard interrupt - exiting...")
        raise KeyboardInterrupt


def storeLiveRaceData(writeAPI):
    try:
        while True:
            client = SignalRClient("unused.txt")
            client.topics = ["Heartbeat", "WeatherData", "RaceControlMessages", "TimingData"]
            overwrite = partial(writeToFile, writeAPI)
            client._to_file = types.MethodType(overwrite,client)
            client.start = types.MethodType(initiateWrite, client)
            client.start()
    except KeyboardInterrupt:
        print('interrupted!')


def storeSimulationData(writeAPI, SimDataFilePath, speedUpFactor=100):
    with open(SimDataFilePath) as file:
        lines = [line.rstrip() for line in file]

    msg = sanitizeJsonData(lines[0])
    cat, msg, dt = json.loads(msg)
    recordedDate = to_datetime(dt)

    for line in lines:
        msg = sanitizeJsonData(line)
        cat, msg, dt = json.loads(msg)
        dt = to_datetime(dt)

        waitingTime = max(0.0, (dt - recordedDate).total_seconds() / speedUpFactor)
        log.debug("Waiting time: %s", waitingTime)
        recordedDate = dt
        time.sleep(waitingTime)

        dt_now = int(time.time() * 1000000000)
        points = messageHandler(cat, msg, dt_now)
        for point in points:
            writeAPI.write(bucket, org, point)


@app.command()
def processLiveData(influxURL="http://localhost:8086"):
    with InfluxDBClient(url=influxURL, token=token, org=org) as client:
        writeAPI = client.write_api(write_options=SYNCHRONOUS)
        storeLiveRaceData(writeAPI)
    return 0


@app.command()
def processSimulationData(path_to_saved_data, influxURL="http://localhost:8086", speedUpFactor: int = 100):
    with InfluxDBClient(url=influxURL, token=token, org=org) as client:
        writeAPI = client.write_api(write_options=SYNCHRONOUS)
        storeSimulationData(writeAPI, path_to_saved_data, speedUpFactor)
    return 0


def main():
    app()


if __name__ == '__main__':
    main()
