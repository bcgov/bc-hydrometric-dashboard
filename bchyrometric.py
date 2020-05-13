import os
import requests
import csv
from contextlib import closing

class CanHydrometrics:
    """
    Class used for interacting with hydrometric api

    Attributes
    ----------
    endpoint: str
        api endpoint url
    sslVerify: Bool
        requests verify should be set to true for production
        ssl error when set to true (server side certificate issue)
    Methods
    --------
    get_level(stationId,start_date,end_date,result_type, sensor-'PRIMARY')
        Gets the current hydrometric level for the selected sensor
    get_flow(stationId,start_date,end_date,result_type, sensor-'PRIMARY')
        Gets the current hydrometric flow
    get_temperature(self,stationId,start_date,end_date,result_type)
        Gets the current station temperature
    """
    endpoint = 'https://vps267042.vps.ovh.ca/scrapi'
    sslVerify = False
    
    def __init__(self,api_key):
        self.api_key = api_key
    
    def get_level(self,stationId,start_date,end_date,result_type,sensor='PRIMARY'):
        # dates as 'YYYY-mm-dd'
        assert result_type in ['stats','history','all']
        payload = {'startDate':start_date,
                    'endDate':end_date,
                    'resultType':result_type,
                    'key':self.api_key}
        level = None
        if sensor.upper() == 'PRIMARY':
            level = 'primarylevel'
        elif sensor.upper() == 'SECONDARY':
            level = 'secondarylevel'
        assert level is not None
        url = f'{self.endpoint}/station/{stationId}/{level}/'
        try:
            # why SSLError 
            r = requests.get(url,params=payload,verify=self.sslVerify)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)
        return r.json()
    def get_flow(self,stationId,start_date,end_date,result_type):
        # dates as 'YYYY-mm-dd'
        assert result_type in ['stats','history','all']
        payload = {'startDate':start_date,
                    'endDate':end_date,
                    'resultType':result_type,
                    'key':self.api_key}
        url = f'{self.endpoint}/station/{stationId}/flow/'
        try:
            r = requests.get(url,params=payload,verify=self.sslVerify)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)
        return r.json()

    def get_temperature(self,stationId,start_date,end_date,result_type):
        # dates as 'YYYY-mm-dd'
        assert result_type in ['stats','history','all']
        payload = {'startDate':start_date,
                    'endDate':end_date,
                    'resultType':result_type,
                    'key':self.api_key}
        url = f'{self.endpoint}/station/{stationId}/temperature/'
        try:
            r = requests.get(url,params=payload,verify=self.sslVerify)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)
        return r.json()
# class CanHydrometricStats:
#     src_hy
if __name__ == '__main__':
    #get_hourly_data_from_csv('08NH005')
    hydro = CanHydrometrics(os.environ['SCRAP2_API_KEY'])
    r = hydro.get_level('08NE074','2020-05-12','2020-05-12',result_type='history')
    print (r)


    