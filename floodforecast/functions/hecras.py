import rascontrol
import os
import xml.etree.ElementTree as ET
import pandas as pd
import json
from ..databases.url_database import _url
from urllib.request import urlopen


class HecRas():
    ''' A class of operating hecras '''

    def __init__(self, rasModelPath, rasInputName, rasPrjName, boundaryXS, waterLevelXS, resultDict, startTime, endTime, version='507'):
        self.rasModelPath = rasModelPath
        self.rasInputName = rasInputName
        self.rasPrjName = rasPrjName
        self.boundaryXS = boundaryXS
        self.boundaryXSList = list(boundaryXS.keys())
        self.waterLevelXS = waterLevelXS
        self.waterLevelXSList = list(waterLevelXS.keys())
        self.resultDict = resultDict
        self.startTime = startTime
        self.endTime = endTime
        self.dateLen = len(pd.date_range(startTime, endTime, freq='H'))
        self.version = version

        self.rasinput()
        self.obsWL = self.currentWaterLevel()
        self.waterLevelDict = self.rasrun()
    
    
    def hmstimer(self, rainDict):
        fmt = '%Y-%m-%d %H:00:00'

        strStartTime = rainDict[list(rainDict.keys())[0]][0]['time']
        strEndTime = rainDict[list(rainDict.keys())[0]][-1]['time']
        
        startTime = datetime(*time.strptime(strStartTime, fmt)[:6])
        EndTime = datetime(*time.strptime(strEndTime, fmt)[:6])

        return startTime, EndTime
    
    
    def rastext(self, datatype):

        if datatype == 'temp':

            tempSeriesList = ['5' if i ==
                              0 else '' for i in range(self.dateLen)]
            tempDurationsList = [f'{self.dateLen}' if i ==
                                 0 else '' for i in range(self.dateLen)]

            tempSeriesStr = ','.join(tempSeriesList)
            tempDurationsStr = ','.join(tempDurationsList)

            return tempSeriesStr, tempDurationsStr

        elif datatype == 'stage':

            stageSeriesList = ['0.1' for i in range(self.dateLen)]
            stageDurationsList = ['1' for i in range(self.dateLen)]

            stageSeriesStr = ','.join(stageSeriesList)
            stageDurationsStr = ','.join(stageDurationsList)

            return stageSeriesStr, stageDurationsStr

        elif datatype == 'flow':
            for xs in self.boundaryXSList:

                if self.boundaryXS[xs]['Boundary_Type'] == 'Stage Series':
                    pass

                if self.boundaryXS[xs]['Boundary_Type'] == 'Flow Series':
                    flowSeriesList = [str(i+10) for i in self.resultDict[xs]]

            flowComIncList = ['1' for i in range(self.dateLen)]
            flowDurationsList = ['1' for i in range(self.dateLen)]

            flowSeriesStr = ','.join(flowSeriesList)
            flowComIncStr = ','.join(flowComIncList)
            flowDurationsStr = ','.join(flowDurationsList)

            return flowSeriesStr, flowComIncStr, flowDurationsStr

        else:
            raise TypeError

    def rasinput(self):
        data = ET.Element('Data')

        info = ET.SubElement(data, 'FileInfo',
                             {'Title': "quasi", 'Version': 'HEC-RAS 5.0.7 March 2019'})
        startDateTime = ET.SubElement(data, 'Start_Date_Time')
        boundaryConditions = ET.SubElement(data, 'Boundary_Conditions')

        temparatureData = ET.SubElement(data, 'Temperature_Data')
        tempTimeReference = ET.SubElement(temparatureData, 'Temp_TimeReference',
                                          {'Type': 'Simulation', 'Date': '06NOV2020', 'Time': '11:00'})
        tempSeries = ET.SubElement(temparatureData, 'Temp_Series')
        tempDuration = ET.SubElement(temparatureData, 'Durations')

        tempSeries.text = self.rastext(datatype='temp')[0]
        tempDuration.text = self.rastext(datatype='temp')[1]

        for xs in self.boundaryXSList:
            # xs stands for cross section
            if self.boundaryXS[xs]['Boundary_Type'] == 'Stage Series':
                node = ET.SubElement(boundaryConditions,
                                     'Node', self.boundaryXS[xs]['Node'])
                boundaryType = ET.SubElement(
                    node, 'Boundary', {'Type': 'Stage Series'})
                date = ET.SubElement(node, 'Date', {'Type': 'Simulation'})
                stage = ET.SubElement(node, 'Stages')
                durations = ET.SubElement(node, 'Durations')

                stage.text = self.rastext(datatype='stage')[0]
                durations.text = self.rastext(datatype='stage')[1]

            if self.boundaryXS[xs]['Boundary_Type'] == 'Flow Series':
                node = ET.SubElement(boundaryConditions,
                                     'Node', self.boundaryXS[xs]['Node'])
                boundaryType = ET.SubElement(
                    node, 'Boundary', {'Type': 'Flow Series'})
                date = ET.SubElement(node, 'Date', {'Type': 'Simulation'})
                flow = ET.SubElement(node, 'Flows')
                compInc = ET.SubElement(node, 'Comp_Inc')
                durations = ET.SubElement(node, 'Durations')

                flow.text = self.rastext(datatype='flow')[0]
                compInc.text = self.rastext(datatype='flow')[1]
                durations.text = self.rastext(datatype='flow')[2]

        tree = ET.ElementTree(data)
        tree.write(os.path.join(self.rasModelPath, self.rasInputName))
        # print('-----------------------------------------------------------------')
        # print(os.path.join(self.rasModelPath, self.rasInputName))

    def currentWaterLevel(self):
        obsWL = {}
        data = urlopen(_url['WL']).read().decode('utf-8')
        output = json.loads(data)
        for i in self.waterLevelXSList:
            for j in range(len(output)):
                if output[j]['stationNo'] == self.waterLevelXS[i]['stationCode']:
                    obsWL[i] = output[j]['last_level']
        # print(obsWL)
        return obsWL

    def rasrun(self):
        rc = rascontrol.RasController(version=self.version)
        rc.open_project(os.path.join(self.rasModelPath, self.rasPrjName))
        rc.run_current_plan()

        waterLevelDict = {}
        for stName in self.waterLevelXSList:
            xs_id = self.waterLevelXS[stName]['Node']['RS']
            river = self.waterLevelXS[stName]['Node']['River']
            reach = self.waterLevelXS[stName]['Node']['Reach']

            intitialWaterLevel = self.obsWL[stName]
            waterLevelDiff = intitialWaterLevel - \
                rc.get_xs(xs_id=xs_id, river=river, reach=reach).value(
                    rc.get_profiles()[25], 2)
            waterLevelList = [
                round(
                    waterLevelDiff + rc.get_xs(xs_id=xs_id, river=river, reach=reach).value(rc.get_profiles()[i], 2), 2) for i in range(25, 49)
            ]
            waterLevelDict[self.waterLevelXS[stName]
                           ['stationCode']] = waterLevelList

        rc.close()

        return waterLevelDict