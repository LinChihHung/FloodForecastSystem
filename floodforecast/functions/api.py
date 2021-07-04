import os
import json


class API():
    def __init__(self, path, pastHours, name, rainDict=None, waterDict=None):
        self.path = os.path.join(path, 'json')
        self.pastHours = pastHours
        self.apiRain(path, rainDict, name, pastHours)
    
    
    def apiTime(self, pastHours, Dict):
        apiTimeDict = {}
        
        startIndex = pastHours
        endIndex = len(Dict[list(Dict.keys())[0]])

        predictTime = Dict[list(Dict.keys())[0]][startIndex-1]['time']
        timeRange = [val['time'] for val in Dict[list(Dict.keys())[0]][startIndex: endIndex]]
              
        apiTimeDict['predict_time'] = predictTime
        apiTimeDict['time'] = timeRange

        return apiTimeDict


    def apiRain(self, path, rainDict, name, pastHours):
        rainfallDict = {}
        if rainDict == []:
            apiRainDict = []
        
        else:
            apiTimeDict = self.apiTime(pastHours, Dict=rainDict)
            for stcode in rainDict.keys():
                rainfall = [val['rainfall'] for val in rainDict[stcode]]
                rainfallDict[stcode] = rainfall
            apiRainDict = [{**apiTimeDict, **rainfallDict}]

        rainPath = os.path.join(self.path, f'rainfall_{name}.json')
        with open(rainPath, 'w') as jsonFile:
            json.dump(apiRainDict, jsonFile)

        return apiRainDict


    def apiWaterLevel(self):
        apiWaterLevelDict = [{**self.apiTimeDict, **self.waterLevelDict}]

        waterLevelPath = os.path.join(self.path, 'waterLevel.json')
        with open(waterLevelPath, 'w') as jsonFile:
            json.dump(apiWaterLevelDict, jsonFile)

        return apiWaterLevelDict