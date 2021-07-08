from ..data.waterlevel_data import _stationDataWater
from ..data.url_data import _url
from ..functions.timer import Timer
from urllib.request import urlopen
from urllib.parse import quote
import json
import copy

class Waterlevel():
    def __init__(self, stationNameList, pastHours, wtrUrl='WL'):
        self.stationNameList = stationNameList
        self.wtrUrl = wtrUrl
        self.timer = Timer()
        self.timer.observe(pastHours=pastHours)


    def obsWaterDict(self):
        obsWaterDict = {}

        obsSrcFormat = self.timer.obsSrcFormat
        obsApiFormat = self.timer.obsApiFormat

        for stName in self.stationNameList:
            rawData = urlopen(_url[self.wtrUrl].format(quote(stName))).read().decode('utf-8')
            output = json.loads(rawData)

            dataList = []
            for dataTimeSrc, dataTimeApi in zip(obsSrcFormat, obsApiFormat):
                information = {}
                information['type'] = 'OBS'
                information['time'] = dataTimeApi
                for data in output:
                    if data['time'] == dataTimeSrc:
                        information['level'] = data['level']
                        break
                    else:
                        information['level'] = -9999
                dataList.append(information)
            obsWaterDict[_stationDataWater[stName]['stationNo']] = dataList
            print(f'station: {stName}, complete (Full water level)')

        return obsWaterDict


    def inputObsWaterDict(self, obsWaterDict):
        inputObsFormat = self.timer.inputObsFormat
        inputObsWaterDict = {}
        
        for stcode in obsWaterDict.keys():
            obsData = obsWaterDict[stcode]

            dataList = []
            for dataTimeInput in inputObsFormat:
                for data in obsData:
                    if data['time'] == dataTimeInput:
                        dataList.append(data)
            inputObsWaterDict[stcode] = dataList

        return inputObsWaterDict


    def initialWaterDict(self):
        '''
        挑出last level, 使模擬的水位可以接上初始水位
        '''
        initialWaterDict = {}
        
        rawData = urlopen('https://iot.thinktron.co/api/data/influxdb/latestWL.php').read().decode('utf-8')
        output = json.loads(rawData)
        for stName in self.stationNameList:
            for data in output:
                if data['station'] == stName:
                  initialWaterDict[_stationDataWater[stName]['stationNo']] = data['last_level']  
            print(f'station: {stName}, complete (Initial water level)')

        return initialWaterDict

if __name__ == '__main__':
    print(_stationDataWater['平林'])
