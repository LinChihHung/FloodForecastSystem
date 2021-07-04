from floodforecast.data.rainstation_data import _stationData
from floodforecast.functions.timer import Timer
from floodforecast.functions.rainfall import Rain
from floodforecast.functions.warning import Warn
from floodforecast.functions.plot import PlotRain
from floodforecast.functions.linenotify import notify
from floodforecast.functions.hechms import HecHms
from floodforecast.functions.api import API
from floodforecast.functions.BME import BME
from datetime import datetime
import os
import json
import time


def warningsystem():
    stationNameList = list(_stationData.keys())
    initialTime = Timer()
    pastHours = 24
    

    '''Rainfall Module'''
    rain = Rain(stationNameList=stationNameList, nowFormat=initialTime.nowFormat, pastHours=pastHours)
    ### observe data ###
    obsRainDict = rain.obsRainDict()
    sumObsRainDict = rain.sumObsRainDict(obsRainDict)

    ### simulate data, from WRF & QPF ###
    simRainDictWRF = rain.simRainDict(simUrl='QPESUMSWRF', futureHoursMax=24)
    inputSimRainDictWRF = rain.inputSimRainDict(simRainDictWRF)
    
    ### Early Warning System and Plot Rainfall Image ###
    sumRainDict = rain.sumRainDict(sumObsRainDict=sumObsRainDict, simRainDict=simRainDictWRF, pastHours=pastHours) 
    warn = Warn(sumRainDict=sumRainDict, notifyHours=6)
    warnStation = warn.warnStation
    warnStrDict = warn.warnStrDict
    if not warnStation:
        pass
    else:
        PlotRain(nowFormat=initialTime.nowFormat, sumRainDict=sumRainDict, stationNameList=warnStation)
    notify(nowFormat=initialTime.nowFormat, warnStrDict=warnStrDict)


    print('-----------------------------------------')
    print('-----------------------------------------')
    print('')
    print(f"Executive Time {datetime.now().strftime('%Y-%m-%d %H:%M:00')}")

def main():
    PROJECTPATH = os.getcwd()
    stationNameList = list(_stationData.keys())
    initialTime = Timer()
    pastHours = 24
    

    '''Rainfall Module'''
    rain = Rain(stationNameList=stationNameList, nowFormat=initialTime.nowFormat, pastHours=pastHours)
    
    ### observe data ###
    obsRainDict = rain.obsRainDict()
    inputObsRainDict = rain.inputObsRainDict(obsRainDict)
    # sumObsRainDict = rain.sumObsRainDict(obsRainDict)
    bmeObsRainDict = rain.bmeObsRainDict(inputObsRainDict=inputObsRainDict, preHours=3)

    ### simulate data, from WRF & QPF ###
    simRainDictWRF = rain.simRainDict(simUrl='QPESUMSWRF', futureHoursMax=24, BME=True)
    # simRainDictQPF = rain.simRainDict(simUrl='QPESUMSQPF', futureHoursMax=24)
    # simRainDictETQPF = rain.simRainDict(simUrl='QPESUMSETQPF', futureHoursMax=24)
    inputSimRainDictWRF = rain.inputSimRainDict(simRainDictWRF)
    # inputSimRainDictQPF = rain.inputSimRainDict(simRainDictQPF)
    # inputSimRainDictETQPF = rain.inputSimRainDict(simRainDictETQPF)

    ### Bayesian Maximum Entropy ###
    BME = BME(stationNameList=stationNameList, bmeObsRainDict=bmeObsRainDict, inputSimRainDict=inputSimRainDictWRF, rainProduct='QPESUMSWRF')
    inputSimRainDictBME = BME.BMEprocess(
        Detrendmethod=0, maxR=None, nrLag=None, rTol=None, maxT=3, ntLag=3, tTol=1.5, 
        EmpCv_parashow=False, EmpCv_picshow=False, CVfit_Sinit_v=None, CVfit_Tinit_v=3, CVfit_plotshow=False,
        BME_nhmax=None, BME_nsmax=None,BME_dmax=None
        )

    # ### Combine Obs & Sim Data ###
    # rainDictWRF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictWRF)
    # rainDictQPF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictQPF)
    # rainDictETQPF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictETQPF)
    # rainDictBME = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictBME)
    # rainDictSet = [rainDictWRF, rainDictQPF, rainDictETQPF, rainDictBME]
    # rainProduct = ['QPESUMSWRF', 'QPESUMSQPF', 'QPESUMSETQPF', 'BME']
    
    # ### Early Warning System and Plot Rainfall Image ###
    # sumRainDict = rain.sumRainDict(sumObsRainDict=sumObsRainDict, simRainDict=simRainDictWRF, pastHours=pastHours) 
    # warn = Warn(sumRainDict=sumRainDict, notifyHours=6)
    # warnStation = warn.warnStation
    # warnStrDict = warn.warnStrDict
    # if not warnStation:
    #     pass
    # else:
    #     PlotRain(nowFormat=initialTime.nowFormat, sumRainDict=sumRainDict, stationNameList=warnStation)
    # notify(nowFormat=initialTime.nowFormat, warnStrDict=warnStrDict)

    ### HEC-HMS & HEC-RAS ###
    # modelPath = {
    #     'hualien': os.path.join(os.getcwd(), 'model', 'hualien', r'C:\Users\User\Desktop\HualienRiver_HMS_0917'), 
    #     'siwkolan': os.path.join(os.getcwd(), 'model', 'siwkolan', '')
    #     }
    # for rain in rainDictSet:
    #     if not rain:
    #         pass
    #     else:
    #         hms = HecHms(path=PROJECTPATH, basin='hualien', rainDict=rainDictWRF, hmsModelPath=modelPath['hualien'], stationNameList=stationNameList)
    # 

    ### API Json ###
    # for (name, rain)  in zip(rainProduct, rainDictSet):
    #     API(path=PROJECTPATH, pastHours=pastHours, name=name, rainDict=rain)

if __name__ == '__main__':
    main()
    # while True:
    #     current = datetime.now()
    #     # if current.minute == 10:
    #     #     main()
    #     if current.minute == 10 or current.minute == 30 or current.minute == 50:
    #         warningsystem()
    #         time.sleep(60)