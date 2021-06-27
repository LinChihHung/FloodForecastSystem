# encoding:utf-8
from linenotipy import Line
from ..data.rainstation_data import _stationData
import os
class notify():
    def __init__(self, nowFormat, warnStrDict):
        self.imgRainPath = os.path.join(os.getcwd(), 'img', nowFormat, 'rain')
        self.linenotify(warnStrDict=warnStrDict)
    
    def linenotify(self, warnStrDict):
        line = Line(token='FRYsdxMysDd4pyL4cJ7a20QgPrtj2qARz7SCxBVxY6r')
        for stcode in warnStrDict.keys():
            message = warnStrDict[stcode]
            imgName = f'{stcode}-{_stationData[stcode]["chineseName"]}.jpg'
            image = os.path.join(self.imgRainPath, imgName)

            line.post(message='測試')
            line.post(message=message, imageFile=image)


