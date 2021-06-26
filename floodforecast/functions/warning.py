# encoding:utf-8
from ..data.rainstation_data import _stationData
import time
class Warn():
    def __init__(self, sumRainDict, pastHours):
        self.sumRainDict = sumRainDict
        self.pastHours = pastHours
        self.warnStrDict = self.warning(sumRainDict, pastHours)
        self.warnStation = list(self.warnStrDict.keys())


    def warning(self, sumRainDict, pastHours):
        warningStrDict = {}
        pastHours = pastHours
        fmt = '%Y-%m-%d %H:00:00'

        for stcode in sumRainDict.keys():
            startIndex = pastHours + 1
            endIndex = len(sumRainDict[stcode])
            chineseName = _stationData[stcode]["chineseName"]
            warningStrList = []
            rainInform = []
            
            # transform string from '%Y-%m-%d %H:00:00' to '%m-%d %H'
            timeFmt = [time.strftime('%m-%d %H',time.strptime(val['time'], fmt)) for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            
            mean01hList = [val['01h_mean'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            mean03hList = [val['03h_mean'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            mean24hList = [val['24h_mean'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]

            max01hList = [val['01h_max'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            max03hList = [val['03h_max'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            max24hList = [val['24h_max'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            
            # heavyRain: 大雨
            # extremeHeavyRain: 豪雨
            # torrentialRain: 大豪雨
            # extremeTorrentialRain: 超大豪雨
            heavyRain01 = False
            heavyRain24 = False
            extremeHeavyRain03 = False
            extremeHeavyRain24 = False
            torrentialRain03 = False
            torrentialRain24 = False
            extremeTorrentialRain24 = False
            
            if any(val >= 40 for val in mean01hList) or any(val >= 40 for val in max01hList):
                heavyRain01 = True
                
            if any(val >= 80 for val in mean24hList) or any(val >= 80 for val in max24hList):
                heavyRain24 = True
            
            if any(val >= 100 for val in mean03hList) or any(val >= 100 for val in max03hList):
                extremeHeavyRain03 = True
                
            if any(val >= 200 for val in mean24hList) or any(val >= 200 for val in max24hList):
                extremeHeavyRain24 = True
            
            if any(val >= 200 for val in mean03hList) or any(val >= 200 for val in max03hList):
                torrentialRain03 = True
            
            if any(val >= 350 for val in mean24hList) or any(val >= 350 for val in max24hList):
                torrentialRain24 = True
            
            if any(val >= 500 for val in mean24hList) or any(val >= 500 for val in max24hList):
                extremeTorrentialRain24 = True
            
            
            if extremeTorrentialRain24:
                warningStrList.append(f'\n{chineseName}測站({stcode})')
                warningStrList.append('24小時累積雨量大於500 mm, 已達超大豪雨等級')
                warningStrList.extend([
                    f'\n{timeFmt[t]}：{mean24hList[t]}-{max24hList[t]} mm/24hr'
                    for t ,(mean24, max24) in enumerate(zip(mean24hList, max24hList))
                ])
                pass
            
            elif torrentialRain03 or torrentialRain24:
                warningStrList.append(f'\n{chineseName}測站({stcode})')
                if torrentialRain03:
                    warningStrList.append('3小時累積雨量大於200 mm')
                if torrentialRain24:
                    warningStrList.append('24小時累積雨量大於350 mm')
                warningStrList.append('已達大豪雨等級')
                warningStrList.extend([
                    f'\n{timeFmt[t]}：{mean03hList[t]}-{max03hList[t]} mm/3hr, {mean24hList[t]}-{max24hList[t]} mm/24hr'
                    for t ,(mean03, max03, mean24, max24) in enumerate(zip(mean03hList, max03hList, mean24hList, max24hList))
                ])
                pass
            
            elif extremeHeavyRain03 or extremeHeavyRain24:
                warningStrList.append(f'\n{chineseName}測站({stcode})')
                if extremeHeavyRain03:
                    warningStrList.append('3小時累積雨量大於100 mm')
                if extremeHeavyRain24:
                    warningStrList.append('24小時累積雨量大於200 mm')
                warningStrList.append('已達豪雨等級')
                warningStrList.extend([
                    f'\n{timeFmt[t]}：{mean03hList[t]}-{max03hList[t]} mm/3hr, {mean24hList[t]}-{max24hList[t]} mm/24hr'
                    for t ,(mean03, max03, mean24, max24) in enumerate(zip(mean03hList, max03hList, mean24hList, max24hList))
                ])
                pass
                
            elif heavyRain01 or heavyRain24:
                warningStrList.append(f'\n{chineseName}測站({stcode})')
                if heavyRain01:
                    warningStrList.append('1小時累積雨量大於40 mm')
                if heavyRain24:
                    warningStrList.append('24小時累積雨量大於80 mm')
                warningStrList.append('已達大雨等級')
                warningStrList.extend([
                    f'\n{timeFmt[t]}：{mean01hList[t]}-{max01hList[t]} mm/hr, {mean24hList[t]}-{max24hList[t]} mm/24hr'
                    for t ,(mean01, max01, mean24, max24) in enumerate(zip(mean01hList, max01hList, mean24hList, max24hList))
                ])
                pass

            else:
                break
            
            warningStr = ' '.join(warningStrList)
            warningStrDict[stcode] = warningStr
        
        return warningStrDict

    
    
