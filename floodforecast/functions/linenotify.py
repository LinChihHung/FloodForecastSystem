# encoding:utf-8
from linenotipy import Line
from ..data.rainstation_data import _stationDataRain
import os
from datetime import datetime, timedelta

class notify():
    def __init__(self, nowFormat, warnStrDict, status=None):
        self.imgRainPath = os.path.join(os.getcwd(), 'img', nowFormat, 'rain')
        self.sendnotify(warnStrDict)
    
    
    def sendnotify(self, warnStrDict):
        if datetime.now().hour == 8 and datetime.now().minute < 20:
            self.linenotify(warnStrDict=warnStrDict, status='goodmorning')

        if not warnStrDict:
            if datetime.now().hour == 16 and datetime.now().minute < 20:
                self.linenotify(warnStrDict=warnStrDict, status='safe16')
            elif datetime.now().hour == 22 and datetime.now().minute < 20:
                self.linenotify(warnStrDict=warnStrDict, status='safe22')
            elif datetime.now().hour == 0 and datetime.now().minute < 20:
                self.linenotify(warnStrDict=warnStrDict, status='goodnight')
        else:
            self.linenotify(warnStrDict=warnStrDict)
    
    
    def linenotify(self, warnStrDict, status=None):
        line = Line(token='FRYsdxMysDd4pyL4cJ7a20QgPrtj2qARz7SCxBVxY6r')
        
        if status == 'goodmorning':
            # 早上的提醒, 跟你說離汛期結束還有多少天
            message = f'\n早安, 離汛期結束還有{self.morning()}天'
            image = os.path.join(os.getcwd(), 'img', 'Line', 'goodmorning.png')
            line.post(message=message, imageFile=image)
        
        elif status == 'safe16':
            # 下午四點的提醒, 提醒大家可以下班了
            message = '\n恭喜各位, 可以安心下班了'
            image = os.path.join(os.getcwd(), 'img', 'Line', 'happyday.png')
            line.post(message=message, imageFile=image)
        
        elif status == 'safe22':
            # 晚上十點的提醒, 提醒大家可以睡覺了
            message = '\n恭喜各位, 可以安心睡覺了'
            image = os.path.join(os.getcwd(), 'img', 'Line', 'sleep.png')
            line.post(message=message, imageFile=image)
        
        elif status == 'goodnight':
            # 叫你去睡覺
            message = '\n晚安, 去睡覺'
            image = os.path.join(os.getcwd(), 'img', 'Line', 'goodnight.png')
            line.post(message=message, imageFile=image)
        
        else:
            message = f'\n{datetime.now().strftime("%Y-%m-%d %H:00:00")}'
            line.post(message=message)
            for stcode in warnStrDict.keys():
                message = warnStrDict[stcode]
                imgName = f'{stcode}-{_stationDataRain[stcode]["chineseName"]}.jpg'
                image = os.path.join(self.imgRainPath, imgName)

                line.post(message=message, imageFile=image)
    

    def morning(self):
        today = datetime.today()
        endTime = datetime(today.year, 11, 30, 23, 59, 59)
        countdown = endTime - datetime.today() + timedelta(days=1)

        return countdown.days


