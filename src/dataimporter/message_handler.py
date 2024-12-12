import logging
from influxdb_client import Point, WritePrecision

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


driverInfoList = [[44, 'HAM', 'Mercedes', '#6CD3BF', 'SOLID'], [63, 'RUS', 'Mercedes', '#6CD3BF', 'DOT'],
                  [55, 'SAI', 'Ferrari', '#F91536', 'DOT'], [16, 'LEC', 'Ferrari', '#F91536', 'SOLID'],
                  [1, 'VER', 'Red Bull', '#3671C6', 'SOLID'], [11, 'PER', 'Red Bull', '#3671C6', 'DOT'],
                  [81, 'PIA', 'McLaren', '#F58020', 'DOT'], [4, 'NOR', 'McLaren', '#F58020', 'SOLID'],
                  [14, 'ALO', 'Aston Martin', '#358C75', 'SOLID'], [18, 'STR', 'Aston Martin', '#358C75', 'DOT'],
                  [10, 'GAS', 'Alpine', '#2293D1', 'SOLID'], [31, 'OCO', 'Alpine', '#2293D1', 'DOT'],
                  [22, 'TSU', 'RB', '#5E8FAA', 'SOLID'], [3, 'RIC', 'RB', '#5E8FAA', 'DOT'],
                  [27, 'HUL', 'Haas F1 Team', '#B6BABD', 'SOLID'], [20, 'MAG', 'Haas F1 Team', '#B6BABD', 'DOT'],
                  [24, 'ZHO', 'Kick Sauber', '#C92D4B', 'DOT'], [77, 'BOT', 'Kick Sauber', '#C92D4B', 'SOLID'],
                  [2, 'SAR', 'Williams', '#37BEDD', 'DOT'], [23, 'ALB', 'Williams', '#37BEDD', 'SOLID']]


def driverInfoLookup(driverNumber: str) -> str:
    for entry in driverInfoList:
        if str(entry[0]) == driverNumber:
            return entry[1]
    log.warning("Driver not found %s", driverNumber)
    return "UKN"


def fetchLastLapTimeData(message):
    results = []
    items = message["Lines"].items()
    for driverNumber, value in items:
        if "LastLapTime" in value:
            if "Value" in value["LastLapTime"]:
                result = driverNumber, lapTime(value["LastLapTime"]["Value"])
                results.append(result)
    return results


def fetchGapToLeaderData(message):
    results = []
    items = message["Lines"].items()
    for driverNumber, value in items:
        if "GapToLeader" in value and value["GapToLeader"] != "":
            result = driverNumber, value["GapToLeader"]
            results.append(result)
    return results


def fetchNumberOfLapsData(message):
    results = []
    items = message["Lines"].items()
    for driverNumber, value in items:
        if "NumberOfLaps" in value and value["NumberOfLaps"] != "":
            result = driverNumber, value["NumberOfLaps"]
            results.append(result)
    return results


def fetchGapToPreviousPositionData(message):
    results = []
    items = message["Lines"].items()
    for driverNumber, value in items:
        if "IntervalToPositionAhead" in value:
            if "Value" in value["IntervalToPositionAhead"] and value["IntervalToPositionAhead"]["Value"] != "":
                result = driverNumber, timeInterval(value["IntervalToPositionAhead"]["Value"])
                results.append(result)
    return results


def fetchSpeedTrapData(message):
    results = []
    items = message["Lines"].items()
    for driverNumber, value in items:
        if "Speeds" in value:
            speedValues = list(value['Speeds'].items())
            for position, carSpeed in speedValues:
                if position == 'ST' and 'Value' in carSpeed and carSpeed['Value'] != "":
                    results.append((driverNumber, int(carSpeed['Value'])))
    return results


def lapTime(time) -> float:
    m, remain = time.split(':')
    s, ms = remain.split(".")
    return int(m) * 60 + int(s) + int(ms) / 1000


def timeInterval(time) -> float:
    if "LAP" in time:
        return 0.0
    if " L" in time:
        return 500.0
    s, ms = time.replace("+", "").split('.')
    return int(s) + int(ms) / 1000


def convertTimeInterval(time) -> float:
    if time[0] == "+":
        return time[1:]
    return time


def fetchTimingData(value, datetime):
    points = []
    try:
        # Last lap time
        LastLapTimeList = fetchLastLapTimeData(value)
        if len(LastLapTimeList) > 0:
            for LastLapTimeItr in LastLapTimeList:
                driverNumber, carSpeed = LastLapTimeItr
                driverName = driverInfoLookup(driverNumber)
                log.info("Last lap: %s - %s", driverName, carSpeed)

                point = Point("lastLapTime") \
                    .field("LastLapTime", carSpeed) \
                    .tag("driver", driverName) \
                    .time(datetime, WritePrecision.NS)
                points.append(point)

        # GapToLeader
        GapToLeaderList = fetchGapToLeaderData(value)
        if len(GapToLeaderList) > 0:
            for GapToLeaderItr in GapToLeaderList:
                driverNumber, gap = GapToLeaderItr
                driverName = driverInfoLookup(driverNumber)
                log.info("Gap to Leader: %s - %s", driverName, gap)

                point = Point("gapToLeader") \
                    .field("GapToLeader", timeInterval(gap)) \
                    .field("GapToLeaderHumanReadable", convertTimeInterval(gap)) \
                    .tag("driver", driverName) \
                    .time(datetime, WritePrecision.NS)
                points.append(point)

        # IntervalToPositionAhead
        GapToPreviousPositionList = fetchGapToPreviousPositionData(value)
        if len(GapToPreviousPositionList) > 0:
            for GapToPreviousPositionItr in GapToPreviousPositionList:
                driverNumber, interval = GapToPreviousPositionItr
                driverName = driverInfoLookup(driverNumber)
                log.info("Gap to Leader: %s - %s", driverName, interval)

                point = Point("intervalToPositionAhead") \
                    .field("IntervalToPositionAhead", interval) \
                    .tag("driver", driverName) \
                    .time(datetime, WritePrecision.NS)
                points.append(point)

        # NumberOfLaps
        NumberOfLapsList = fetchNumberOfLapsData(value)
        if len(NumberOfLapsList) > 0:
            for NumberOfLapsItr in NumberOfLapsList:
                driverNumber, lapNumber = NumberOfLapsItr
                driverName = driverInfoLookup(driverNumber)
                log.info("NumberOfLaps: %s - %s", driverName, lapNumber)

                point = Point("numberOfLaps") \
                    .field("NumberOfLaps", lapNumber) \
                    .tag("driver", driverName) \
                    .time(datetime, WritePrecision.NS)
                points.append(point)

        # Speed trap
        SpeedTrapList = fetchSpeedTrapData(value)
        if len(SpeedTrapList) > 0:
            for SpeedTrapItr in SpeedTrapList:
                driverNumber, carSpeed = SpeedTrapItr
                driverName = driverInfoLookup(driverNumber)
                log.info("Speed trap: %s - %s", driverName, carSpeed)

                point = Point("speedTrap") \
                    .field("Speed", carSpeed) \
                    .tag("driver", driverName) \
                    .time(datetime, WritePrecision.NS)
                points.append(point)
    except Exception as e:
        log.exception("Unable to extract TimingData: %s %s", value, e)

    return points


def fetchMessagesFromRaceControl(value, datetime):
    try:
        rcm = list(value["Messages"].values())[0]["Message"]
        log.info("RaceControlMessage: %s", rcm)

        point = Point("raceControlMessage") \
            .field("Message", rcm) \
            .time(datetime, WritePrecision.NS)
        return [point]
    except Exception as e:
        log.exception("Unable to extract RaceControlMessages: %s %s", value, e)
        return []


def fetchWeatherData(value, datetime):
    try:
        w = value
        log.info("WeatherData: %s", w)

        point = Point("weatherData") \
            .field("AirTemp", float(w["AirTemp"])) \
            .field("Humidity", float(w["Humidity"])) \
            .field("Pressure", float(w["Pressure"])) \
            .field("Rainfall", float(w["Rainfall"])) \
            .field("TrackTemp", float(w["TrackTemp"])) \
            .field("WindDirection", float(w["WindDirection"])) \
            .field("WindSpeed", float(w["WindSpeed"])) \
            .time(datetime, WritePrecision.NS)
        return [point]
    except Exception as e:
        log.exception("Unable to extract WeatherData: %s %s", value, e)
        return []


def messageHandler(key, message, datetime) -> list:
    if key == 'TimingData':
        return fetchTimingData(message, datetime)
    elif key == 'RaceControlMessages':
        return fetchMessagesFromRaceControl(message, datetime)
    elif key == 'WeatherData':
        return fetchWeatherData(message, datetime)
    else:
        return []
