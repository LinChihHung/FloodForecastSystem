from floodforecast.functions.waterlevel import Waterlevel
# from floodforecast.functions.database import dict_to_db
from floodforecast.data.rainstation_data import _stationDataRain
from floodforecast.data.waterlevel_data import _stationDataWater
from floodforecast.functions.timer import Timer
from floodforecast.functions.rainfall import Rain
from floodforecast.functions.warning import Warn
from floodforecast.functions.plot import PlotRain
from floodforecast.functions.linenotify import notify
from floodforecast.functions.hechms import HecHms
from floodforecast.functions.api import API
from floodforecast.functions.BME import BME
from floodforecast.data.hualienRas_database import _hualienBoundaryXS, _hualienWaterLevelXS
from floodforecast.data.siwkolanRas_database import _siwkolanBoundaryXS, _siwkolanWaterLevelXS
from datetime import datetime
import os
import json
import time


def main():
    PROJECTPATH = os.getcwd()
    rainStationNameList = list(_stationDataRain.keys())
    waterStationNameList = list(_stationDataWater.keys())
    initialTime = Timer()
    pastHours = 24


    '''Rainfall Module'''
    rain = Rain(stationNameList=rainStationNameList, nowFormat=initialTime.nowFormat, pastHours=pastHours)
    rainProduct = ['QPESUMSWRF', 'QPESUMSQPF', 'QPESUMSETQPF', 'BME']
    
    ### observe data ###
    obsRainDict = rain.obsRainDict()
    inputObsRainDict = rain.inputObsRainDict(obsRainDict)
    sumObsRainDict = rain.sumObsRainDict(obsRainDict)
    # bmeObsRainDict = rain.bmeObsRainDict(inputObsRainDict=inputObsRainDict, preHours=3)
    # obs data to database
    # print('Add obsevre Data to Database')
    # dict_to_db(dataDict=obsRainDict, tableName='obs_rainfall')

    ### simulate data, from WRF & QPF ###
    simRainDictWRF = rain.simRainDict(simUrl='QPESUMSWRF', futureHoursMax=24, BME=True)
    simRainDictQPF = rain.simRainDict(simUrl='QPESUMSQPF', futureHoursMax=24)
    simRainDictETQPF = rain.simRainDict(simUrl='QPESUMSETQPF', futureHoursMax=24)
    inputSimRainDictWRF = rain.inputSimRainDict(simRainDictWRF)
    inputSimRainDictQPF = rain.inputSimRainDict(simRainDictQPF)
    inputSimRainDictETQPF = rain.inputSimRainDict(simRainDictETQPF)

    ### Bayesian Maximum Entropy ###
    # BMERain = BME(stationNameList=rainStationNameList, bmeObsRainDict=bmeObsRainDict, inputSimRainDict=inputSimRainDictWRF, rainProduct='QPESUMSWRF')
    # inputSimRainDictBME = BMERain.BMEprocess(
    #     Detrendmethod=0, maxR=None, nrLag=None, rTol=None, maxT=3, ntLag=3, tTol=1.5, 
    #     EmpCv_parashow=False, EmpCv_picshow=False, CVfit_Sinit_v=None, CVfit_Tinit_v=3, CVfit_plotshow=False,
    #     BME_nhmax=None, BME_nsmax=None,BME_dmax=None
    #     )
    # with open(os.path.join(PROJECTPATH, 'BMEtest', f'{initialTime.nowFormat}.json'), 'w') as f:
    #     json.dump(inputSimRainDictBME, f)

    ### Combine Obs & Sim Data ###
    rainDictWRF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictWRF)
    rainDictQPF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictQPF)
    rainDictETQPF = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictETQPF)
    # rainDictBME = rain.combineRainDict(obsRainDict=inputObsRainDict, simRainDict=inputSimRainDictBME)
    
    ### inputSimRainDictSet & rainDictSet ###
    rainDictSet = [rainDictWRF, rainDictQPF, rainDictETQPF]
    inputSimRainDictSet = [inputSimRainDictWRF, inputSimRainDictQPF, inputSimRainDictETQPF]
    
    
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


    '''----------------------------------------------------------------------------------------------------------------------------------'''
    '''----------------------------------------------------------------------------------------------------------------------------------'''
    '''Water Level Modelu'''
    water = Waterlevel(stationNameList=waterStationNameList, pastHours=pastHours)
    obsWaterDict = water.obsWaterDict()
    initialWaterDict = water.initialWaterDict()
    inputObsWaterDict = water.inputObsWaterDict(obsWaterDict=obsWaterDict)

    # ### HEC-HMS & HEC-RAS ###
    hmsModelPath = {
        'hualien': os.path.join(os.getcwd(), 'model', 'HMS', 'hualien', '2021.03.17_HLBridge'), 
        'siwkolan': os.path.join(os.getcwd(), 'model', 'HMS', 'siwkolan', '2021.04.05_Siwkolan')
        }
    rasModelPath = {
        'hualien': os.path.join(os.getcwd(), 'model', 'hualien', r'C:\Users\User\Desktop\HualienRiver_HMS_0917'),
        'siwkolan': os.path.join(os.getcwd(), 'model', 'siwkolan', '')
    }
    crossSection = {
        'hualien': list(_hualienBoundaryXS.keys()), 
        'siwkolan': list(_siwkolanBoundaryXS.keys())
    }
    print(crossSection['hualien'])

    for rain in rainDictSet:
        if not rain:
            pass
        else:
            # Hualien
            hmsHualien = HecHms(
                path=PROJECTPATH, basin='hualien', rainDict=rainDictWRF, hmsModelPath=hmsModelPath['hualien'], 
                stationNameList=rainStationNameList, crossSectionList=crossSection['hualien'],
                )
    #         rasHualien = HecRas(path=PROJECTPATH, basin='hualien', rainDict=rainDictWRF, hmsModelPath=hmsModelPath['hualien'], stationNameList=stationNameList)
            # Siwkolan
            hmsSiwkolan = HecHms(
                path=PROJECTPATH, basin='siwkolan', rainDict=rainDictWRF, hmsModelPath=hmsModelPath['siwkolan'], 
                stationNameList=rainStationNameList, crossSectionList=crossSection['siwkolan'],
                )

    # ### API Json ###
    # for (name, rain)  in zip(rainProduct, rainDictSet):
    #     API(path=PROJECTPATH, pastHours=pastHours, name=name, rainDict=rain)
    
    print('')
    print('')
    print('-----------------------------------------')
    print('-----------------------------------------')
    print('')
    print(f"Executive Time {datetime.now().strftime('%Y-%m-%d %H:%M:00')}")

if __name__ == '__main__':
    main()
    # while True:
    #     current = datetime.now()
    #     if current.minute == 10:
    #         main()
    #         time.sleep(30)
        # if current.minute == 10 or current.minute == 30 or current.minute == 50:
        #     main()
        #     # warningsystem()
        #     time.sleep(60)