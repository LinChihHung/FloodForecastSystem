import sys
import numpy as np
import pandas as pd
import stamps
import matplotlib.pyplot as plt
from stamps.general.valstvgx import valstv2stg
from scipy.spatial.distance import pdist
from stamps.stats import stcov,stcovfit,mlecovfit
from stamps.graph.modelplot import modelplot
from stamps.bme.softconverter import ud2zs
from stamps.bme.BMEoptions import BMEoptions
from stamps.bme.BMEprobaEstimations import BMEPosteriorMoments
from stamps.stest.stmean import stmean,stmeaninterp
from stamps.stest.kernelsmoothing import kernelsmoothing,kernelsmoothing_est


class BMEestimation():
    def __init__(self, Points, Z, EstPiont, DetrendMethod='STmean'):
        '''
        points is nx3 numpy array. column is X Y T.
        EstPiont is nx3 numpy array. column is X Y T.
        '''
        # HardDataInput
        X, Y, T = Points[:, 0], Points[:, 1], Points[:, 2]
        ch = np.hstack((X.reshape(-1, 1), Y.reshape(-1, 1), T.reshape(-1, 1)))
        zh = Z.reshape(-1, 1).copy()
        Z_, cMS, tME,_ = valstv2stg(ch, zh)
        self.Z = Z_
        self.cMS = cMS
        self.tME = tME
        
        # make estimated grid input
        self.grid_input(EstPiont)
        
        # Detrend 
        self.Detrend(method=DetrendMethod)
        self.grid_trendest(Detrendtype=DetrendMethod)
        
        
    def Detrend(self,method='STmean'):
        if method in [0]:
            self.Zmean = 0
            self.Zres = self.Z.copy()
            self.Detrendtype = 0
        elif method in ['STmean', ] :
            ms, mss, mt, mts, Zmean = stmean(self.cMS, self.tME, self.Z)
            self.Zmean = Zmean
            self.Zres = self.Z - Zmean
            self.Detrendtype = 1
        ch_ = np.asarray(list(zip(np.tile(self.cMS[:,0], self.tME.size), np.tile(self.cMS[:,1], self.tME.size), \
                                            self.tME.repeat(self.cMS.shape[0]))))
        self.ch = ch_[~np.isnan(self.Zres.ravel()),:]
        self.zh = self.Zres.reshape(-1, 1)[~np.isnan(self.Zres.ravel()),:]


    def grid_input(self,EstPiont):
        df = pd.DataFrame(EstPiont,columns = ['X', 'Y', 'T'])
        self.ck = df.sort_values(by=['T', 'Y', 'X'], ascending=[True, False, True]).values
        self.grid_xyi = (pd.DataFrame(self.ck[:, :2]).drop_duplicates()).values
        self.ckt = np.array(list(set(self.ck[:, -1].ravel().tolist()))).reshape(-1, 1)

       
    def grid_trendest(self,Detrendtype):
        if Detrendtype in [0]:
            gridmean = 0
        elif Detrendtype in ['STmean',1] :
            gridmean = stmeaninterp(self.cMS, self.tME, self.Z, self.grid_xyi, self.ckt.reshape(-1))
        self.gridmean = gridmean


    def Empirical_covplot(self, maxR=None, nrLag=None, rTol=None, maxT=None,
                          ntLag=None, tTol=None, parashow=False, picshow=False):
        '''

        Parameters:

            maxR: int. 
            Spatial Distance Limit

            nrLag: int. 
            Number of spatial lag

            rTol: int. 
            Spatial lag tolerance

            maxT: int. 
            Temporal Distance Limit

            ntLag: int. 
            Number of temporal lag    

            tTol: int. 
            Temporal lag tolerance

        '''
        # Spatial part
        if maxR is None:
            maxR = pdist(self.cMS).max()   
        if nrLag is None:
            nrLag = 10
        if rTol is None:
            rTol = pdist(self.cMS).max()/20   

        # Temporal part
        if maxT is None:
            maxT = pdist(np.hstack((self.tME.reshape(-1, 1), np.ones((len(self.tME), 1))))).max()
        if ntLag is None:
            ntLag = 10
        if tTol is None:
            tTol = maxT/20

        rLag = np.linspace(0, maxR, nrLag)
        rLagTol = rTol*np.ones(rLag.size)
        tLag = np.linspace(0, maxT, ntLag)
        tLagTol = tTol*np.ones(tLag.size)
 
        if parashow:
            print('(maxR,nrLag,rTol) = ', (maxR, nrLag, rTol))
            print('(maxT,ntLag,tTol) = ', (maxT, ntLag, tTol))
        C, npairs, lagSS, lagTT = stcov.stcov(self.cMS, self.tME, self.Zres, rLag, rLagTol, tLag, tLagTol)
        _ = modelplot(C, [rLag,tLag], show=picshow);
        plt.close()
        self.C = C
        self.lagSS = lagSS
        self.lagTT = lagTT
        self.npairs = npairs


    def covpar_make(self, covmodelcode):
        '''
        1: exponentialC
        2: gaussianC 
        3: sphericalC
        4: holecosC
        5: nuggetC
        6: maternC
        '''
        ModelDict = {1:'exponentialC', 2:'gaussianC', 3:'sphericalC', 4:'holecosC', 5:'nuggetC', 6:'maternC'}
        covmodel = []
        for i in covmodelcode:
            if 0 in i:
                break
            else:
                covmodel_ = [ModelDict[i[0]] + '/' + ModelDict[i[1]]]
                covmodel.append(covmodel_)

        return covmodel


    def Covmodel_Autofit(self, covmodel, covparam0, method='BOBYQA'):
        '''
        method:
        1 = BOBYQA method
        2 = MLE method
        '''
        covmodel = self.covpar_make(covmodel)
        for i in np.arange(len(covparam0)):
            covparam0[i][1] = [covparam0[i][1]]
            covparam0[i][2] = [covparam0[i][2]]

        if method in ['BOBYQA', 1]:
            print ("Fitting covariance model with BOBYQA:")
            covparam,optval = stcovfit.covmodelfit(self.lagSS, self.lagTT, self.C, self.npairs, covmodel, covparam0)
            # optval smaller is better
            return covparam, optval


    def Covmodelfitting(self, Sinit_v=None, Tinit_v=None, plotshow = False):
        '''
        Sinit_v is initial guess of spatial relative lenth
        Tinit_v is initial guess of temporal relative lenth       
        '''

        Scv,Tcv = np.meshgrid(range(1,4), range(1,4))
        STcvPool = np.vstack((Scv.ravel(), Tcv.ravel())).T
        optval_list = []
        covparam_list = []
        covmodel_list = []
        if Sinit_v is None:
            Sinit_v = pdist(self.cMS).max()/2
        if Tinit_v is None:
            Tinit_v = len(self.tME)/2
            
        for STcv in STcvPool:
            covmodel = [STcv]
            covparam = [[self.C[0][0], Sinit_v, Tinit_v]]
            covparam_fit,optval = self.Covmodel_Autofit(covmodel, covparam, method='BOBYQA')
            optval_list.append(optval)
            covparam_list.append(covparam_fit)
            covmodel_list.append(covmodel)

        optvalar = np.array(optval_list)
        bestoc_order = np.where(optvalar==optvalar.min())[0][0]
        covmodel = self.covpar_make(covmodel_list[bestoc_order])
        covparam = covparam_list[bestoc_order]
        if plotshow:
            c = modelplot(self.C, [self.lagSS[:,0], self.lagTT[0,:]], covmodel, covparam, show=False);
        self.covmodel = covmodel.copy()
        self.covparam = covparam.copy()

        return covmodel,covparam


    def BMEestimationH(self, nhmax=None, nsmax=None, dmax=None):

        #BME parameter preparation
        if nhmax is None:
            nhmax = 5
        if nsmax is None:
            nhmax = 3
        if dmax is None:
            dmaxs = self.covparam[0][1][0]
            dmaxt = self.covparam[0][2][0]
            dmax = np.array([[dmaxs+5000, dmaxt+5,1000]])
            print('Strongly suggest to set the dmax by yourself')

        order = np.nan
        options = BMEoptions()
        options[0,0] = 1
        print ("Start BME estimation...")
        moments = BMEPosteriorMoments(self.ck, ch=self.ch, cs=None, zh=self.zh, zs=None, \
        covmodel=self.covmodel, covparam=self.covparam, nhmax=nhmax, nsmax=nsmax, \
        dmax=dmax, order=order, options=options)

        self.moments = moments

        Zres_est, ckMS, cktME, __ = valstv2stg(self.ck, moments[:,0:1])
        Zest = Zres_est + self.gridmean
        BMEresult = pd.DataFrame(np.hstack((self.ck, Zest.T.reshape(-1,1))))
        BMEresult.columns = ['X','Y','T','bmeZest']
        
        return BMEresult