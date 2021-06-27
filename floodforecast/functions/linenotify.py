# encoding:utf-8
from linenotipy import Line
from ..data.rainstation_data import _stationData
import os
from datetime import datetime
class notify():
    def __init__(self, nowFormat, warnStrDict, status=None):
        self.imgRainPath = os.path.join(os.getcwd(), 'img', nowFormat, 'rain')
        self.sendnotify(warnStrDict)
    
    
    def sendnotify(self, warnStrDict):
        if not warnStrDict:
            if datetime.now().hour == 16 and datetime.now().minute < 20:
                self.linenotify(warnStrDict=warnStrDict, status='safe16')
            elif datetime.now().hour == 22 and datetime.now().minute < 20:
                self.linenotify(warnStrDict=warnStrDict, status='safe22')
        else:
            self.linenotify(warnStrDict=warnStrDict)
    
    
    def linenotify(self, warnStrDict, status=None):
        line = Line(token='FRYsdxMysDd4pyL4cJ7a20QgPrtj2qARz7SCxBVxY6r')
        
        if status == 'safe16':
            message = '\n恭喜各位, 可以安心下班了'
            image = os.path.join(os.getcwd(), 'img', 'Line', 'happyday.png')
            line.post(message=message, imageFile=image)
        elif status == 'safe22':
            message = '\n恭喜各位, 可以安心睡覺了'
            image = os.path.join(os.getcwd(), 'img', 'Line', 'sleep.png')
            line.post(message=message, imageFile=image)
        else:
            for stcode in warnStrDict.keys():
                message = warnStrDict[stcode]
                imgName = f'{stcode}-{_stationData[stcode]["chineseName"]}.jpg'
                image = os.path.join(self.imgRainPath, imgName)

                line.post(message='測試')
                line.post(message=message, imageFile=image)


