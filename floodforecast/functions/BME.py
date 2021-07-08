# from ..data.rainstation_data import _stationDataRain
import os
import twd97
import json
import os,twd97,json
import pandas as pd
import numpy as np
import copy
from datetime import datetime, timedelta
from ..data.rainstation_data import _stationDataRain
from ..functions.BMEFunction import BMEestimation

class BME:
    def __init__(self, stationNameList, bmeObsRainDict, inputSimRainDict, rainProduct, estTlen=6):
        self.stationNameList = stationNameList
        self.bmeObsRainDict = bmeObsRainDict
        self.inputSimRainDict = copy.deepcopy(inputSimRainDict)
        self.rainProduct = rainProduct
        self.timeList = [val['time'] for val in bmeObsRainDict[self.stationNameList[0]]]
        self.simTlen = len(inputSimRainDict[self.stationNameList[0]])
        self.estTlen = 6
        self.csvPath = os.path.join(os.getcwd(), 'floodforecast', 'data', 'csv')


    def BMEformatter(self, dataframe, points):
        lng84Series = dataframe.loc[points].iloc[:, 0]
        lat84Series = dataframe.loc[points].iloc[:, 1]
        pdict_v = dataframe.loc[points].iloc[:, 2]
        
        lng97List = []
        lat97List = []
        for lat, lng in zip(lat84Series, lng84Series):
            x, y = twd97.fromwgs84(lat, lng)
            lng97List.append(x)
            lat97List.append(y)
        lngSeries = pd.Series(lng97List)
        latSeries = pd.Series(lat97List)

        return lngSeries, latSeries, pdict_v

    
    def GetBMESimInput(self, stcode):
        # get forcasting value and location by given grid points and CSV file
        points = _stationDataRain[stcode]['points']
        obsValue = [val['rainfall'] for val in self.bmeObsRainDict[stcode]]
        stPdict = pd.DataFrame([])
        
        for i, (t, val) in enumerate(zip(self.timeList, obsValue)):
            GetDataTimeFormat = pd.Timestamp(t).strftime('%Y%m%d%H')
            GetDataTimePath = os.path.join(self.csvPath, f'{GetDataTimeFormat}_{self.rainProduct}.csv')
            dataframe = pd.read_csv(GetDataTimePath)
            x, y , pdict_v = self.BMEformatter(dataframe=dataframe, points=points)
            aStPdict = pd.DataFrame(np.vstack((x.values, y.values, (i+1)*np.ones(x.shape),
                                val*np.ones(x.shape), pdict_v.values)).T, index=points)
            stPdict = pd.concat((stPdict, aStPdict), axis=0)
        stPdict.columns = ['X', 'Y', 'T', 'Z_obs', 'Z_p']
        stPdict = stPdict.assign(Z=stPdict['Z_obs'] - stPdict['Z_p'])

        return stPdict
    

    def CreatGridInput(self, stPdict):
        # creat grid
        pointsXYdf = stPdict[['X', 'Y']].drop_duplicates().reset_index()
        pointsXYdf.columns = ['points', 'X', 'Y']
        tME = np.arange(len(self.timeList)+1, len(self.timeList)+1+self.estTlen)
        gridXY = np.tile(pointsXYdf[['X', 'Y']].values, (len(tME), 1))
        gridT = np.repeat(tME, len(pointsXYdf))

        return gridXY[:,0], gridXY[:,1], gridT
    

    def BMEpostprocess(self, stcode, stPdict, BMEresult):
        # BME output arrangement
        pointsXYdf = stPdict[['X','Y']].drop_duplicates().reset_index()
        pointsXYdf.columns = ['points','X','Y']
        BMEresult = BMEresult.merge(pointsXYdf, on=['X','Y'])
        earliestTime = self.timeList[0]
        estT = [str(pd.Timestamp(earliestTime) + timedelta(hours=int(i)-1, minutes=0)) for i in BMEresult['T']]
        BMEresult = BMEresult.assign(realT=estT).sort_values(by=['T', 'points'], ascending=[True, True])
        BMEresult = BMEresult.set_index(BMEresult.pop('points'))
        index = [i for i in file.drop_duplicates(subset ="T").index] + [file.shape[0]]
        for i in range(self.estTlen):
            rawValue = self.inputSimRainDict[stcode][i]['rainfall']
            modifiedValue = np.mean(file['bmeZest'].iloc[index[i]:index[i+1]])
            self.inputSimRainDict[stcode][i]['rainfall'] = rawValue + modifiedValue
        for i in range(self.estTlen, self.simTlen):
            rawValue = self.inputSimRainDict[stcode][i]['rainfall']
            modifiedValue = np.mean(file['bmeZest'].iloc[index[-2]:index[-1]])
            self.inputSimRainDict[stcode][i]['rainfall'] = rawValue + modifiedValue

        # BME input arrangement
        stPdict = stPdict.reset_index()
        stPdict.columns = ['points'] + stPdict.columns[1:].tolist()
        rawT = [str(pd.Timestamp(earliestTime) + timedelta(hours=int(i)-1, minutes=0)) for i in stPdict['T']]
        stPdict = stPdict.assign(realT=rawT).reset_index().sort_values(by=['T', 'points'], ascending=[True, True])
        stPdict = stPdict.set_index(stPdict.pop('points'))

        return self.inputSimRainDict
    

    def BMEprocess(self, Detrendmethod=0, maxR=None, nrLag=None, rTol=None, 
            maxT=3, ntLag=3, tTol=1.5, EmpCv_parashow=False, EmpCv_picshow=False,
            CVfit_Sinit_v=None, CVfit_Tinit_v=3, CVfit_plotshow=False,
            BME_nhmax=None, BME_nsmax=None, BME_dmax=None):
        
        BMEinputdict = {}
        BMEoutputdict = {}
        for stcode in self.stationNameList:
            try:
                ## BME preparation
                stPdict = self.GetBMESimInput(stcode)
                estX, estY, estT = self.CreatGridInput(stPdict)
                points = stPdict[['X', 'Y', 'T']].values# shape must be n*3
                Z = stPdict[['Z']].values.reshape(-1, 1) # shape must be n*1
                EstPoints = np.hstack((estX.reshape(-1, 1), estY.reshape(-1, 1), estT.reshape(-1, 1)))
                
                ## create estimate class
                BMEobject = BMEestimation(points, Z, EstPoints, DetrendMethod=Detrendmethod)
                
                ## calculate emperical covariance
                BMEobject.Empirical_covplot(maxR=maxR, nrLag=nrLag, rTol=rTol, 
                                            maxT=maxT, ntLag=ntLag, tTol=tTol,
                                            parashow=EmpCv_parashow, picshow=EmpCv_picshow)
                
                # Covariance model autofitting
                covmodel, covparam = BMEobject.Covmodelfitting(
                    Sinit_v=CVfit_Sinit_v, 
                    Tinit_v=CVfit_Tinit_v, 
                    plotshow=CVfit_plotshow
                    )
                
                ## BME estimation
                BMEresult = BMEobject.BMEestimationH(
                    nhmax=BME_nhmax, 
                    nsmax=BME_nsmax,
                    dmax=BME_dmax
                    )
                
                ## BME result postprocess
                inputSimRainDictBME = self.BMEpostprocess(stcode, stPdict, BMEresult)
                
                # ## save result to dictionay
                # BMEoutputdict.update({stcode: BMEoutput})
                
                # ## save input data to dictionay
                # BMEinputdict.update({stcode: BMEinput})
            
            except:
                inputSimRainDictBME = self.inputSimRainDict
            
        return inputSimRainDictBME
        


