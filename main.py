from floodforecast.data.rainstation_data import _stationData
from floodforecast.functions.timer import Timer
from floodforecast.functions.rainfall import Rain
from floodforecast.functions.warning import Warn
import json

def main():
    stationNameList = list(_stationData.keys())
    initialTime = Timer()
    pastHours = 24
    

    '''Rainfall Module'''
    rain = Rain(stationNameList=stationNameList, nowFormat=initialTime.nowFormat, pastHours=pastHours)
    
    # # observe data # #
    obsRainDict = rain.obsRainDict()
    # inputObsRainDict = rain.inputObsRainDict(obsRainDict)
    sumObsRainDict = rain.sumObsRainDict(obsRainDict)
    # bmeObsRainDict = rain.bmeObsRainDict(inputObsRainDict=inputObsRainDict, preHours=3)

    # # simulate data, from WRF & QPF # #
    simRainDictWRF = rain.simRainDict(simUrl='QPESUMSWRF', futureHoursMax=24)
    # simRainDictQPF = rain.simRainDict(simUrl='QPESUMSQPF')
    # simRainDictETQPF = rain.simRainDict(simUrl='QPESUMSETQPF')
    # inputSimRainDictWRF = rain.inputSimRainDict(simRainDictWRF)
    # print(inputSimRainDictWRF)

    # # Combine Obs & Sim Data # #
    # rainDictWRF = rain.totalRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictWRF)
    # rainDictQPF = rain.totalRainDict(obsRainDict=inputObsRainDict, simRainDict=simRainDictQPF)
    
    # # Early Warning System and Plot Rainfall # #
    sumRainDict = rain.sumRainDict(sumObsRainDict=sumObsRainDict, simRainDict=simRainDictWRF, pastHours=pastHours) 
    warn = Warn(sumRainDict=sumRainDict, pastHours=pastHours)
    warnStation = warn.warnStation
    warnStrDict = warn.warnStrDict
    if not warnStation:
        pass
    else:
        print('plot rain')

if __name__ == '__main__':
    main()