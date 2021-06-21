from floodforecast.data.rainstation_data import _stationData
from floodforecast.functions.timer import Timer
from floodforecast.functions.rainfall import Rain
import json

def main():
    stationNameList = list(_stationData.keys())
    initialTime = Timer()

    '''Rainfall Module'''
    rain = Rain(stationNameList=stationNameList, nowFormat=initialTime.nowFormat)
    
    # # observe data # #
    obsRainDict = rain.obsRainDict()
    # inputObsRainDict = rain.inputObsRainDict(obsRainDict)
    warnObsRainDict = rain.warnObsRainDict(obsRainDict)
    # print(warnObsRainDict)
    # bmeObsRainDict = rain.bmeObsRainDict(inputObsRainDict=inputObsRainDict, preHours=3)

    # # simulate data, from WRF & QPF # #
    simRainDictWRF = rain.simRainDict(simUrl='QPESUMSWRF')
    # simRainDictQPF = rain.simRainDict(simUrl='QPESUMSQPF')
    # simRainDictETQPF = rain.simRainDict(simUrl='QPESUMSETQPF')
    # inputSimRainDictWRF = rain.inputSimRainDict(simRainDictWRF)
    # print(simRainDictWRF)

    # # Combine Obs & Sim Data # #
    # rainDictWRF = rain.totalRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictWRF)
    # rainDictQPF = rain.totalRainDict(obsRainDict=inputObsRainDict, simRainDict=simRainDictQPF)
    # with open('test.json', 'w', encoding='utf-8') as jsonFile:
        # json.dump(rainDictWRF, jsonFile, ensure_ascii=False)
    
    # # Early Warning System # #
    warnRainDict = rain.warnRainDict(warnObsRainDict=warnObsRainDict, simRainDict=simRainDictWRF) 
    with open('test.json', 'w', encoding='utf-8') as jsonFile:
        json.dump(rainDictWRF, jsonFile, ensure_ascii=False)

if __name__ == '__main__':
    main()