import json
from typing import List

import typer

from dataimporter.message_handler import driverInfoList

app = typer.Typer()


@app.command()
def addDriverTeamColor(dashboardJsonFilePath: str, dashboardTitles: List[str]):
    driverTeamColorList = []
    for driverInfoItr in driverInfoList:
        driverTeamColorList.append(
            matchDriverTeamColor(driverInfoItr[1], driverInfoItr[3], driverInfoItr[4] == 'DOT'))
    print(json.dumps(driverTeamColorList))

    driverNames = [driver[1] for driver in driverInfoList]
    print(driverNames)

    with open(dashboardJsonFilePath, "r") as dashboard:
        dashboardContents = dashboard.read()
    parsedJsonData = json.loads(dashboardContents)

    # print(parsedJsonData)
    i = 0
    for panel in parsedJsonData['panels']:
        if panel['title'] in dashboardTitles and 'fieldConfig' in panel and 'overrides' in panel[
            'fieldConfig']:
            print("==================", panel['title'], "==================")
            driverTeamColor = [o for o in panel['fieldConfig']['overrides']
                                              if 'matcher' not in o
                                              or 'id' not in o['matcher']
                                              or o['matcher']['id'] != 'byName'
                                              or 'options' not in o['matcher']
                                              or o['matcher']['options'] not in driverNames
                                              ]

            print("================== driverTeamColor ==================")
            print(driverTeamColor)

            print("================== new driverTeamColor ==================")
            driverTeamColor.extend(driverTeamColorList)
            print(driverTeamColor)
            parsedJsonData['panels'][i]['fieldConfig']['overrides'] = driverTeamColor
        i += 1

    # Writing to sample.json
    with open(dashboardJsonFilePath, "w") as dashboard:
        dashboard.write(json.dumps(parsedJsonData, indent=4))


def matchDriverTeamColor(driverName, driverTeamColorHexValue, dottedLine=False):
    if dottedLine:
        return {
            "matcher": {
                "id": "byName",
                "options": driverName
            },
            "properties": [
                {
                    "id": "color",
                    "value": {
                        "fixedColor": driverTeamColorHexValue,
                        "mode": "fixed"
                    }
                }, {
                    "id": "custom.lineStyle",
                    "value": {
                        "dash": [
                            0,
                            5
                        ],
                        "fill": "dot"
                    }
                }
            ]
        }
    else:
        return {
            "matcher": {
                "id": "byName",
                "options": driverName
            },
            "properties": [
                {
                    "id": "color",
                    "value": {
                        "fixedColor": driverTeamColorHexValue,
                        "mode": "fixed"
                    }
                }
            ]
        }


def main():
    app()


if __name__ == '__main__':
    main()
