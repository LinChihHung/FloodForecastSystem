# url for rainfall data
# sim rainfall data's url are QPESUMSQPF and QPESUMSWRF, the data is provide by manysplendid's api
# obs rainfall data's url is from CWB (中央氣象局),  the data is provide by thinktron's api

_url = {
    'QPESUMSQPF': 'http://fsv.manysplendid.com.tw/rfd-grid/QPESUMS_QPF/',
    'QPESUMSWRF': 'http://fsv.manysplendid.com.tw/rfd-grid/QPESUMS_WRF/',
    'QPESUMSETQPF': 'http://fsv.manysplendid.com.tw/rfd-grid/QPESUMS_ETQPF/',
    'CWB': 'https://iot.thinktron.co/api/data/influxdb/RF.php?stationId={}',
    'WL': 'https://iot.thinktron.co/api/data/influxdb/WL.php?station={}'
}