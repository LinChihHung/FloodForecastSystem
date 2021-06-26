from ..functions.timer import Timer
from ..data.url_data import _url
from ..data.rainstation_data import _stationData
from bs4 import BeautifulSoup
from urllib.request import urlopen
from collections import defaultdict
import json
from numpy import mean
import os
from datetime import datetime, timedelta
from pandas import date_range
from zipfile import ZipFile
from io import BytesIO
import re
import pandas as pd
import copy

class Rain():
    def __init__(self, stationNameList, nowFormat, pastHours, obsUrl='CWB'):
        self.stationNameList = stationNameList
        self.nowFormat = nowFormat
        self.obsUrl = obsUrl
        self.timer = Timer()
        self.timer.observe(pastHours=pastHours)
    

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


    def sumObsRainDict(self, obsRainDict):
        warnObsFormat = self.timer.warnObsFormat
        warnObsRainDict = copy.deepcopy(obsRainDict)
        
        for stcode in self.stationNameList:
            obsData = warnObsRainDict[stcode]
            warnObsRainDict[stcode] = []
            
            dataList = []
            for dataTimeInput in warnObsFormat:
                for data in obsData:
                    if data['time'] == dataTimeInput:
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
            print(f"Warning!! {simUrl} doesn't exist. It will return any emty list")
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
                    meanValue = round(mean([float(i) for i in simRainDataFrame.loc[forecastPoint].iloc[:, 2]]), 1)
                    maxValue = max([float(i) for i in simRainDataFrame.loc[forecastPoint].iloc[:, 2]])
                    information = {}
                    information['type'] = simUrl
                    information['time'] = dataTimeApi                
                    information['01h_mean'] = meanValue
                    information['01h_max'] = maxValue
                        
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
        if simRainDict == []:
            pass
        else:
            inputSimRainDict = copy.deepcopy(simRainDict)
            newKey = 'rainfall'
            oldKey = '01h_mean'

            for stcode in self.stationNameList:
                simData = inputSimRainDict[stcode]

                for data in simData:
                    data[newKey] = data.pop(oldKey)
                    del data['01h_max']
        
        return inputSimRainDict

   
    def combineRainDict(self, obsRainDict, simRainDict):
        combineRainDict = copy.deepcopy(obsRainDict)
        
        for stcode in obsRainDict.keys():
            combineRainDict[stcode].extend(simRainDict[stcode])
        
        return combineRainDict


    def sumRainDict(self, sumObsRainDict, simRainDict, pastHours):
        sumRainDict = self.combineRainDict(sumObsRainDict, simRainDict)
        
        for key in sumRainDict.keys():
            startIndex = pastHours + 1
            endIndex = len(sumRainDict[key])
            
            # repalce -9999 to 0
            sumRainDict[key] = [{k:0 if v == -9999 else v for k, v in item.items()} for item in sumRainDict[key]]
            # add all value into a list
            meanList = [val['01h'] if val['type'] == 'OBS' else val['01h_mean'] for val in sumRainDict[key]]
            maxList = [val['01h'] if val['type'] == 'OBS' else val['01h_max'] for val in sumRainDict[key]]
            for num in range(startIndex, endIndex):
                # Count 3 hours sum
                sumRainDict[key][num]['03h_mean'] = round(sum(meanList[num-2: num+1]))
                sumRainDict[key][num]['03h_max'] = round(sum(maxList[num-2: num+1]))
                # Count 6 hours sum
                sumRainDict[key][num]['06h_mean'] = round(sum(meanList[num-5: num+1]))
                sumRainDict[key][num]['06h_max'] = round(sum(maxList[num-5: num+1]))
                # Count 12 hours sum
                sumRainDict[key][num]['12h_mean'] = round(sum(meanList[num-11: num+1]))
                sumRainDict[key][num]['12h_max'] = round(sum(maxList[num-11: num+1]))
                # Count 24 hours sum
                sumRainDict[key][num]['24h_mean'] = round(sum(meanList[num-23: num+1]))
                sumRainDict[key][num]['24h_max'] = round(sum(maxList[num-23: num+1]))
                # Count 48 hours sum, if data length is smaller than 48 hours, then the value is nan
                if num-47 < 0:
                    sumRainDict[key][num]['48h_mean'] = -9999
                    sumRainDict[key][num]['48h_max'] = -9999
                else:
                    sumRainDict[key][num]['48h_mean'] = round(sum(meanList[num-47: num+1]))
                    sumRainDict[key][num]['48h_max'] = round(sum(maxList[num-47: num+1]))
                # Count 72 hours sum, if data length is smaller than 72 hours, then the value is nan
                if num-71 < 0:
                    sumRainDict[key][num]['72h_mean'] = -9999
                    sumRainDict[key][num]['72h_max'] = -9999
                else:
                    sumRainDict[key][num]['72h_mean'] = round(sum(meanList[num-71: num+1]))
                    sumRainDict[key][num]['72h_max'] = round(sum(maxList[num-71: num+1]))        
        
        return sumRainDict


if __name__ == '__main__':
    pass

