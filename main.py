from floodforecast.data.rainstation_data import _stationData
from floodforecast.functions.timer import Timer
from floodforecast.functions.rainfall import Rain
from floodforecast.functions.warning import Warn
from floodforecast.functions.plot import PlotRain
from floodforecast.functions.linenotify import notify
import json

def main():
    stationNameList = list(_stationData.keys())
    initialTime = Timer()
    pastHours = 24
    

    '''Rainfall Module'''
    rain = Rain(stationNameList=stationNameList, nowFormat=initialTime.nowFormat, pastHours=pastHours)
    
    ### observe data ###
    obsRainDict = rain.obsRainDict()
    inputObsRainDict = rain.inputObsRainDict(obsRainDict)
    sumObsRainDict = rain.sumObsRainDict(obsRainDict)
    bmeObsRainDict = rain.bmeObsRainDict(inputObsRainDict=inputObsRainDict, preHours=3)

    ### simulate data, from WRF & QPF ###
    simRainDictWRF = rain.simRainDict(simUrl='QPESUMSWRF', futureHoursMax=24)
    simRainDictQPF = rain.simRainDict(simUrl='QPESUMSQPF')
    simRainDictETQPF = rain.simRainDict(simUrl='QPESUMSETQPF')
    inputSimRainDictWRF = rain.inputSimRainDict(simRainDictWRF)
    inputSimRainDictQPF = rain.inputSimRainDict(simRainDictQPF)

    ### Combine Obs & Sim Data ###
    rainDictWRF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictWRF)
    rainDictQPF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictQPF)
    
    ### Early Warning System and Plot Rainfall ###
    sumRainDict = rain.sumRainDict(sumObsRainDict=sumObsRainDict, simRainDict=simRainDictWRF, pastHours=pastHours) 
    warn = Warn(sumRainDict=sumRainDict, pastHours=pastHours)
    warnStation = warn.warnStation
    warnStrDict = warn.warnStrDict
    if not warnStation:
        pass
    else:
        PlotRain(nowFormat=initialTime.nowFormat, sumRainDict=sumRainDict, stationNameList=warnStation)
        notify(nowFormat=initialTime.nowFormat, warnStrDict=warnStrDict)

if __name__ == '__main__':
    main()