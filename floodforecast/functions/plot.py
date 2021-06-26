import os
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdate


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
    def __init__(self, nowFormat, stationNameList):
        super().__init__(nowFormat)
        self.imgRainPath = self.mkImgRainDir()
        self.plotrain(stationNameList, sumRainDict)
        

    def mkImgRainDir(self):
        imgRainPath = os.path.join(self.imgPath, 'rain')
        if os.path.exists(imgPath):
            pass
        else:
            os.mkdir(imgRainPath)

        return imgRainPath

    
    def plotrain(stationNameList, sumRainDict):




if __name__ == '__main__':
    PlotRain('20210202', test='test')


# class PlotWater(Plot):
#     def __init__(self):
#         pass