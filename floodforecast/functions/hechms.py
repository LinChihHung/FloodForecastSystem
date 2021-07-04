from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer
import os
import numpy as np
import time
from datetime import datetime

class HecHms():
    """A class for operating hechms model"""
     
    def __init__(self, path, basin, rainDict, hmsModelPath, stationNameList, controlName='Current', rainfallFileName='rainfallHms.dss'):
        self.path = path
        self.basin = basin
        self.startTime, self.endTime = self.hmstimer(rainDict)
        self.gagePath, self.rainfallPath, self.controlPath, self.resultPath = self.hmssetup(hmsModelPath, controlName, rainfallFileName)
        self.hmsrain(stationNameList, rainDict)
        self.hmsgage(stationNameList=stationNameList)
        self.hmscontrol()
        self.hmsrun(path, basin)



    def hmstimer(self, rainDict):
        fmt = '%Y-%m-%d %H:00:00'

        strStartTime = rainDict[list(rainDict.keys())[0]][0]['time']
        strEndTime = rainDict[list(rainDict.keys())[0]][-1]['time']
        
        startTime = datetime(*time.strptime(strStartTime, fmt)[:6])
        EndTime = datetime(*time.strptime(strEndTime, fmt)[:6])

        return startTime, EndTime
    

    def pathname(
        self, location, 
        group='Hualien', parameter='PRECIP-INC', interval='1HOUR', description='RainGage', 
        dss=True, flow=False
        ):
        # hec pathname = /A/B/C/D/E/F/
        # A = group, B = location, C = parameter, D = window, E = interval, F = description
        # pathname example: /Hualien/stationName/PRECIP-INC/10Nov2020 - 11Nov2020/1HOUR/RainGage/
        
        if dss == True and flow == False:
            # pathname for "input" dss file
            # pathname format: /A/B/C//E/F/
            # input *.dss doesn't contain D part
            pathname = f'/{group}/{location}/{parameter}//{interval}/{description}/'

        elif dss == True and flow == True:
            # pathname for "output" dss file
            # pathname format: //B/C//E/F/
            # output *.dss is create by hechms model.
            # Pathnames don't contain A and D part, parameter and description will change as well.
            parameter = 'FLOW-COMBINE'
            description = f'RUN:{self.controlName.upper()}'
            pathname = f'//{location}/{parameter}//{interval}/{description}/'

        elif dss == False and flow == False:
            # pathname for gage file
            # pathname format: /A/B/C/D/E/F/
            # *.gage contain D part in pathname, D part is the time window of rainfall
            window = ' '.join([self.startTime.strftime(
                '%d%b%Y'), '-', self.endTime.strftime('%d%b%Y')])
            pathname = f'/{group}/{location}/{parameter}/{window}/{interval}/{description}/'

        else:
            raise Exception("not the right combination")

        return pathname


    def hmssetup(self, hmsModelPath, controlName, rainfallFileName):
        
        # list all file name in hms model folder
        listDir = os.listdir(hmsModelPath)
        print(listDir)

        gageFileName = [i for i in listDir if i.endswith('.gage')]
        gageFilePath = os.path.join(hmsModelPath, gageFileName[0])

        rainfallFilePath = os.path.join(hmsModelPath, rainfallFileName)

        controlFileName = f'{controlName}.control'
        controlFilePath = os.path.join(hmsModelPath, controlFileName)

        resultFileName = f'{controlName}.dss'
        resultFilePath = os.path.join(hmsModelPath, resultFileName)

        if os.path.exists(resultFilePath):
            os.remove(resultFilePath)
        else:
            pass

        return gageFilePath, rainfallFilePath, controlFilePath, resultFilePath


    def hmsrain(self, stationNameList, rainDict, units='MM', type='PER-CUM'):
        # input rainfall data into dss file
        for stcode in stationNameList:

            rainPathname = self.pathname(location=stcode, dss=True, flow=False)
            values = [i['rainfall'] for i in rainDict[stcode]]
            shape = len(values)

            # write data into dss file
            tsc = TimeSeriesContainer()
            tsc.pathname = rainPathname
            tsc.startDateTime = '{}:00:00'.format(
                self.startTime.strftime('%d%b%Y %H'))
            tsc.units = units
            tsc.type = type
            tsc.numberValues = shape
            tsc.values = values

            fid = HecDss.Open(self.rainfallPath)
            fid.deletePathname(tsc.pathname)
            fid.put_ts(tsc)
            ts = fid.read_ts(rainPathname)
            fid.close()

        return
    
    
    def hmsgage(self, stationNameList):

        with open(self.gagePath, 'r') as f:
            gageText = f.readlines()
        for stcode in stationNameList:
            gagePathname = self.pathname(location=stcode, dss=False)
            try:
                index = gageText.index('Gage: {}\n'.format(stcode))
                DSSFileNameIndex = next(
                    gageText.index(i) for i in gageText[index:] if i.find('DSS File Name') != -1
                )
                DSSPathnameIndex = next(
                    gageText.index(i) for i in gageText[index:] if i.find('DSS Pathname') != -1
                )
                StartTimeIndex = next(
                    gageText.index(i) for i in gageText[index:] if i.find('Start Time') != -1
                )
                EndTimeIndex = next(
                    gageText.index(i) for i in gageText[index:] if i.find('End Time') != -1
                )

                gageText[DSSFileNameIndex] = f'       DSS File Name: {self.rainfallPath}\n'
                gageText[DSSPathnameIndex] = f'       DSS Pathname: {gagePathname}\n'
                gageText[StartTimeIndex] = f'       Start Time: {self.startTime.strftime("%d %B %Y, %H:00 ")}\n'
                gageText[EndTimeIndex] = f'       End Time: {self.endTime.strftime("%d %B %Y, %H:00 ")}\n'
            except:
                pass
        with open(self.gagePath, 'w') as f:
            for item in gageText:
                f.write(item)


    def hmscontrol(self):

        with open(self.controlPath, 'r') as f:
            controlText = f.readlines()

        startDateIndex = next(
            controlText.index(i) for i in controlText if i.find('Start Date') != -1
        )
        startTimeIndex = next(
            controlText.index(i) for i in controlText if i.find('Start Time') != -1
        )
        endDateIndex = next(
            controlText.index(i) for i in controlText if i.find('End Date') != -1
        )
        endTimeIndex = next(
            controlText.index(i) for i in controlText if i.find('End Time') != -1
        )

        controlText[startDateIndex] = f'     Start Date: {self.startTime.strftime("%d %B %Y")}\n'
        controlText[startTimeIndex] = f'     Start Time: {self.startTime.strftime("%H:00")}\n'
        controlText[endDateIndex] = f'     End Date: {self.endTime.strftime("%d %B %Y")}\n'
        controlText[endTimeIndex] = f'     End Time: {self.endTime.strftime("%H:00")}\n'

        with open(self.controlPath, 'w') as f:
            for item in controlText:
                f.write(item)


    def hmsrun(self, path, basin):
        if basin == 'hualien':
            executefilePath = os.path.abspath(
                r"floodforecast\functions\hualien_engine.py")
            os.chdir(r'C:\Program Files\HEC\HEC-HMS\4.5')
            os.system(r'.\HEC-HMS.cmd -script {}'.format(executefilePath))
        
        elif basin == 'siwkolan':
            executefilePath = os.path.abspath(
                r"floodforecast\functions\siwkolan_engine.py")
            os.chdir(r'C:\Program Files\HEC\HEC-HMS\4.5')
            os.system(r'.\HEC-HMS.cmd -script {}'.format(executefilePath))            
        
        else:
            print('Error!! Wrong basin.')
            raise ValueError
        
        os.chdir(path)
