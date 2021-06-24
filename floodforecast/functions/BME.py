# from ..data.rainstation_data import _stationData
import os
import twd97
import pandas as pd
import json

class BME:
    def __init__(self, stationNameList, bmeObsRainDict, inputSimRainDict):
        self.stationNameList = stationNameList
        self.bmeObsRainDict = bmeObsRainDict
        self.inputSimRainDict = inputSimRainDict
        self.csvPath = os.path.join(os.getcwd(), 'floodforecast', 'data', 'csv')


    def BMEformatter(self, dataframe, points):
        lng84Series = dataframe.loc[points].iloc[:, 0]
        lat84Series = dataframe.loc[points].iloc[:, 1]
        
        lng97List = []
        lat97List = []
        for lat, lng in zip(lat84Series, lng84Series):
            x, y = twd97.fromwgs84(lat, lng)
            lng97List.append(x)
            lat97List.append(y)
        lngSeries = pd.Series(lng97List)
        latSeries = pd.Series(lat97List)

        return lngSeries, latSeries


    # def BMEpreprocess(self, ):



if __name__ == '__main__':
    # f = open(os.getcwd() + r'\test.json', encoding='utf-8')
    # test = json.load(f)
    # townList = test.keys()
    # for town in townList:
    #     for stcode in test[town].keys():
    #         print(stcode)

    stationNameList = []
    obsRainDict = []
    simRainDict = []

    test = BME(stationNameList=stationNameList, bmeObsRainDict=obsRainDict, inputSimRainDict=simRainDict)
    dataframe = pd.read_csv(test.csvPath + r'\2021061717.csv')
    points = [7237, 7238, 7239, 7140, 7141, 7142, 7143, 7144]
    x, y = test.BMEformatter(dataframe=dataframe, points=points)
    print(x, y)
    for stcode in stationNameList:
        points = _stationData[stcode]['points']

