from datetime import datetime, timedelta
from pandas import date_range

class Timer:
    def __init__(self):
        self.initial()
    
    def initial(self):
        rawTime = datetime.now()
        
        self.nowTime = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=10 + rawTime.minute % 10)
        # self.nowTime = datetime(year=2021, month=6, day=21, hour=16)
        self.nowFormat = self.nowTime.strftime('%Y%m%d%H')


    def observe(self, pastHours=24):
        self.startTime = self.nowTime - timedelta(hours=pastHours)
        
        # Original Data, extract every 10 minutes data, freq='10min'
        # obsDateRange: 10 minutes date range
        # obsSrcFormat: format of the observe data sources' api from thinktron (興創)
        # obsApiFormat: format of the api we launch for thinktron
        self.obsDateRange = date_range(self.startTime, self.nowTime, freq='10min')
        self.obsSrcFormat = [i.strftime('%Y-%m-%dT%H:%M:00+08:00') for i in self.obsDateRange]
        self.obsApiFormat = [i.strftime('%Y-%m-%d %H:%M:00') for i in self.obsDateRange]

        # Input Data, extract every hourly data, freq='H'
        # hrObsDateRange: hourly date range
        # inputObsFormat: format on the hour, ex: 2021-06-20 17:00:00, 2021-06-20 18:00:00, 2021-06-20 19:00:00
        # warnObsFormat: format not on the hour ex: 2021-06-20 17:10:00, 2021-06-20 18:10:00, 2021-06-20 19:10:00
        self.hrObsDateRange = date_range(self.startTime, self.nowTime, freq='H')
        self.inputObsFormat = [i.strftime('%Y-%m-%d %H:00:00') for i in self.hrObsDateRange]
        self.warnObsFormat = [i.strftime('%Y-%m-%d %H:%M:00') for i in self.hrObsDateRange]


    def simulate(self, futureHours):
        self.endTime = self.nowTime + timedelta(hours=futureHours)

        # Simulate Data, extract every hourly data, freq='H'
        # simDateRange: Hourly date range, start from nowTime+1, nowTime consider as obs data
        # simSrcFormat: format of the simulate data sources' api from manysplendid (多采)
        # simApiFormat: format of the api we launch for thinktron
        self.simDateRange = date_range(self.nowTime, self.endTime, freq='H')[1:]
        self.simSrcFormat = [i.strftime('%Y%m%d%H') for i in self.simDateRange]
        self.simApiFormat = [i.strftime('%Y-%m-%d %H:00:00') for i in self.simDateRange]

if __name__ == '__main__':
    times = Timer()
    times.observe()