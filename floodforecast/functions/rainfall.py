from ..functions.timer import Timer
from ..data.url_data import _url
from ..data.rainstation_data import _stationData
from bs4 import BeautifulSoup
from urllib.request import urlopen
from collections import defaultdict
import json
from numpy import mean, nan
import os
from datetime import datetime, timedelta
from pandas import date_range
from zipfile import ZipFile
from io import BytesIO
import re
import pandas as pd
import copy

class Rain():
    def __init__(self, stationNameList, nowFormat, obsUrl='CWB'):
        self.stationNameList = stationNameList
        self.nowFormat = nowFormat
        self.obsUrl = obsUrl
        self.timer = Timer()
        self.timer.observe()
    
    def obsRainDict(self):
        obsRainDict = {}
        
        obsSrcFormat = self.timer.obsSrcFormat
        obsApiFormat = self.timer.obsApiFormat
        
        for stcode in self.stationNameList:
            rawData = urlopen(_url[self.obsUrl].format(stcode)).read().decode('utf-8')
            output = json.loads(rawData)

            dataList = []
            for dataTimeSrc, dataTimeApi in zip(obsSrcFormat, obsApiFormat):
                information = {}
                information['type'] = 'OBS'
                information['time'] = dataTimeApi
                for data in output:
                    if data['time'] == dataTimeSrc:
                        information['010m'] = data['010m']
                        information['01h'] = data['01h']
                        information['03h'] = data['03h']
                        information['06h'] = data['06h']
                        information['12h'] = data['12h']
                        information['24h'] = data['24h']
                        break
                    else:
                        information['010m'] = -9999
                        information['01h'] = -9999
                        information['03h'] = -9999
                        information['06h'] = -9999
                        information['12h'] = -9999
                        information['24h'] = -9999
                dataList.append(information)
            obsRainDict[stcode] = dataList
        
        return obsRainDict


    def inputObsRainDict(self, obsRainDict):
        inputObsFormat = self.timer.inputObsFormat
        inputObsRainDict = copy.deepcopy(obsRainDict)

        for stcode in self.stationNameList:
            obsData = inputObsRainDict[stcode]
            inputObsRainDict[stcode] = []

            dataList = []
            for dataTimeInput in inputObsFormat:
                for data in obsData:
                    if data['time'] == dataTimeInput:
                        # add key 'rainfall' equal 01h value
                        data['rainfall'] = data['01h']
                        # deelte key which unuse
                        del data['010m']
                        del data['01h']
                        del data['03h']
                        del data['06h']
                        del data['12h']
                        del data['24h']

                        dataList.append(data)
            
            inputObsRainDict[stcode] = dataList
        
        return inputObsRainDict


    def warnObsRainDict(self, obsRainDict):
        warnObsFormat = self.timer.warnObsFormat
        warnObsRainDict = copy.deepcopy(obsRainDict)
        
        for stcode in self.stationNameList:
            obsData = warnObsRainDict[stcode]
            warnObsRainDict[stcode] = []
            
            dataList = []
            for dataTimeInput in warnObsFormat:
                for data in obsData:
                    if data['time'] == dataTimeInput:
                        # add key 'rainfall' equal 01h value
                        data['rainfall'] = data['01h']
                        # deelte key which unuse
                        del data['010m']

                        dataList.append(data)
            
            warnObsRainDict[stcode] = dataList
        
        return warnObsRainDict
    

    def bmeObsRainDict(self, inputObsRainDict, preHours=3):
        '''
        bmeObsRainDict: A dictionary format for BME input, only contain a few obs data ahead current time
        inputObsRainDict: dictiionary, from input dictionary, hourly data
        preHours: int, defined how many hours ahead current time
        '''
        bmeObsRainDict = copy.deepcopy(inputObsRainDict)
        
        for stcode in self.stationNameList:
            inputData = bmeObsRainDict[stcode]
            bmeObsRainDict[stcode] = []

            dataList = []
            for bmeTime in range(preHours*(-1), 0):
                dataList.append(inputData[bmeTime])
            
            bmeObsRainDict[stcode] = dataList
        
        return bmeObsRainDict

    
    def simRainDict(self, simUrl, futureHoursMax=24):
        simRainDict = {}
        try:
            data = urlopen(os.path.join(_url[simUrl], self.nowFormat)).read().decode('utf-8')
            forecastLen = len(BeautifulSoup(data, 'html.parser').findAll('a')) - 1
            if forecastLen > futureHoursMax:
                futureHours = futureHoursMax
            else:
                futureHours = forecastLen            
            simFlag = True        
        except:
            simFlag = False
                
        if simFlag:
            self.timer.simulate(futureHours=futureHours)
            simApiFormat = self.timer.simApiFormat

            zipName = 'grid_rain_0000.0{:0>2d}{}'
            for num, dataTimeApi in enumerate(simApiFormat):
                data = urlopen(os.path.join(
                    _url[simUrl], self.nowFormat, zipName.format(num + 1, '.zip')))
                zipfile = ZipFile(BytesIO(data.read()))
                rawFile = []

                for line in zipfile.open(zipName.format(num + 1, '')).readlines():
                    rawData = re.split('\r|    |  ', line.decode('utf-8'))[0:3]
                    rawFile.append(rawData)
                simRainDataFrame = pd.DataFrame(
                    rawFile[5:], columns=['Longtitude', 'Latitude', 'intensity (mm/hr)']
                )
                if num == 0:
                    fileName = str(int(self.nowFormat)+1) + '.csv'
                    csvPath = os.path.join(os.getcwd(), 'floodforecast', 'data', 'csv', fileName)
                    simRainDataFrame.to_csv(csvPath, index=None)

            
                for stcode in self.stationNameList:
                    if num == 0:
                        simRainDict[stcode] = []
                    
                    dataList = []
                    forecastPoint = _stationData[stcode]['points']
                    meanValue = round(mean([float(i) for i in simRainDataFrame.loc[forecastPoint].iloc[:, 2]]), 2)
                    maxValue = max([float(i) for i in simRainDataFrame.loc[forecastPoint].iloc[:, 2]])
                    information = {}
                    information['type'] = simUrl
                    information['time'] = dataTimeApi                
                    information['mean'] = meanValue
                    information['max'] = maxValue
                        
                    dataList.append(information)
                    simRainDict[stcode].extend(dataList)
        else:
            simRainDict = []
        return simRainDict
    

    def inputSimRainDict(self, simRainDict):
        '''
        change simRainDict into inputSimRainDict
        1. Change key name from 'mean' to 'rainfall'
        2. delete unuse key 'max'
        '''
        inputSimRainDict = copy.deepcopy(simRainDict)
        newKey = 'rainfall'
        oldKey = 'mean'

        for stcode in self.stationNameList:
            simData = inputSimRainDict[stcode]

            for data in simData:
                data[newKey] = data.pop(oldKey)
                del data['max']
        
        return inputSimRainDict

   
    def combineRainDict(self, obsRainDict, simRainDict):
        combineRainDict = copy.deepcopy(obsRainDict)
        
        for stcode in obsRainDict.keys():
            combineRainDict[stcode].extend(simRainDict[stcode])
        
        return combineRainDict


    def warnRainDict(self, warnObsRainDict, simRainDict):
        warnRainDict = self.combineRainDict(warnObsRainDict, simRainDict)

        return warnRainDict


if __name__ == '__main__':
    pass

