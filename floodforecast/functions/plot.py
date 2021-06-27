import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from datetime import timedelta
from pandas import date_range
import numpy as np
import os
from datetime import datetime
from ..data.rainstation_data import _stationData
import time


class Plot():
    def __init__(self, nowFormat):
        self.nowFormat = nowFormat
        self.imgPath = self.mkImgDir()
    
    def mkImgDir(self):
        imgPath = os.path.join(os.getcwd(), 'img', self.nowFormat)
        if os.path.exists(imgPath):
            pass
        else:
            os.mkdir(imgPath)
        
        return imgPath

class PlotRain(Plot):
    def __init__(self, nowFormat, sumRainDict, stationNameList):
        super().__init__(nowFormat)
        self.imgRainPath = self.mkImgRainDir()
        self.plotrain(sumRainDict, stationNameList)
        

    def mkImgRainDir(self):
        imgRainPath = os.path.join(self.imgPath, 'rain')
        if os.path.exists(imgRainPath):
            pass
        else:
            os.mkdir(imgRainPath)

        return imgRainPath

    
    def plotrain(self, sumRainDict, stationNameList):
        fmt = '%Y-%m-%d %H:00:00'
        for stcode in stationNameList:
            fig, ax = plt.subplots(figsize=(16, 9))
            plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
            plt.rcParams['xtick.labelsize'] = 16
            plt.rcParams['ytick.labelsize'] = 16
            plt.rcParams['axes.axisbelow'] = True

            chineseName = _stationData[stcode]['chineseName']
            dateRange = [datetime(*time.strptime(val['time'], fmt)[:6]) for val in sumRainDict[stcode] if val['type'] != 'OBS']
            mean01hList = [val['01h_mean'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            mean03hList = [val['03h_mean'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]
            mean24hList = [val['24h_mean'] for val in sumRainDict[stcode] if val['type'] != 'OBS' ]

            width = np.min(np.diff(mdate.date2num(dateRange)))
            if all(i <= 40 for i in mean01hList):
                bar = ax.bar(dateRange, mean01hList, width=width, 
                            label='降雨量', edgecolor='k')
                ax.set_yticks(np.arange(0, 55, 5))
            else:
                bar = ax.bar(dateRange, mean01hList, width=width, 
                            label='降雨量', edgecolor='k')

            ax.set_xlabel('時間 (mm-dd hh)', fontsize=24, weight="bold")
            ax.set_ylabel("降雨量 (mm)", fontsize=24, weight="bold")
            ax.set_title(f'{chineseName}測站({stcode})雨量預報', fontsize=32, weight="bold")
            ax.grid()


            ax2 = ax.twinx()
            if all(i <= 40 for i in mean03hList) and all(i <= 40 for i in mean24hList):
                ax2.plot(dateRange, mean03hList, label='3小時累積雨量',
                        color='tab:brown', linewidth=3, marker='o', linestyle='dashed')
                ax2.plot(dateRange, mean24hList, label='24小時累積雨量',
                        color='tab:orange', linewidth=3, marker='o', linestyle='dashed')
                ax2.set_ylim(ymax=50)
            else:
                ax2.plot(dateRange, mean03hList, label='3小時累積雨量',
                        color='tab:brown', linewidth=3, marker='o', linestyle='dashed')
                ax2.plot(dateRange, mean24hList, label='24小時累積雨量',
                        color='tab:orange', linewidth=3, marker='o',linestyle='dashed')
                ax2.set_ylim(ymax = max(mean03hList + mean24hList) + 20)

            ax2.set_ylabel("累積雨量 (mm)", fontsize=24, weight="bold")
            ax2.set_ylim(ymin=0)

            # Set legend for ax & ax2
            handles1, labels1 = ax.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            handles = [handles1[0], handles2[0], handles2[1]]
            labels = [labels1[0], labels2[0], labels2[1]]
            ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(0, 1), bbox_transform=ax.transAxes, 
            fontsize=16, edgecolor='k')
            # ax.legend(handles, labels, loc='upper left', bbox_to_anchor=(0, 0, 1, 1), fontsize=16, ncol=3, 
            # columnspacing=1, handlelength=0.5, handletextpad=0.5, edgecolor='k')
            
            fig.tight_layout()
            saveName = os.path.join(
                self.imgRainPath, stcode + '-' + _stationData[stcode]['chineseName']
                )
            fig.savefig(f'{saveName}.jpg', dpi=330)
            plt.close(fig)





if __name__ == '__main__':
    PlotRain('20210202', test='test')


# class PlotWater(Plot):
#     def __init__(self):
#         pass