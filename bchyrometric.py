import os
import requests
import csv
from contextlib import closing
import sqlite3
from datetime import date

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
    
    def __init__(self,api_key, hydat_database = 'data/BC_Hydat.sqlite3'):
        self.api_key = api_key
        self.db = hydat_database
    
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
    def get_historic(self,stationId,start_date,end_date,record_type='FLOW'):
        """ Returns historic flow or level or for station
        parameters
        ----------
            stationId: str, '08NE074'
            start_date:  str, 'YYYY-mm-dd'
            end_date: str, 'YYYY-mm-dd'
            record_type: str, 'FLOW'
        """
        yr = date.today().year
        # only months matter with the historic data... but easiest to have date objects for selection
        y,m,d = start_date.split('-')
        start = date(yr,int(m),int(d))
        y,m,d = end_date.split('-')
        end = date(yr,int(m),int(d))
        date_string_field_name = 'RECORD_DATE'
        date_string = f"{yr}||'-'||CAST(MONTH as TEXT)||'-'||CAST(DAY as TEXT) {date_string_field_name}"
        field_list = ['STATION_NUMBER','MONTH','DAY',record_type+'_MIN',record_type+'_MAX',record_type+'_25PERC',record_type+'_MEDIAN',record_type+'_75PERC']
        fields = ','.join(field_list)
        sql = f"SELECT {date_string},{fields} FROM DLY_FLOW_LEVELS_STATS WHERE STATION_NUMBER =?"
        field_list = [date_string_field_name] + field_list
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        t = (stationId,)
        json_data = []
        for row in c.execute(sql,t):
            d = {}
            for c,f in zip(list(row),field_list):
                d[f]=c
            record_date = date(yr,d['MONTH'],d['DAY'])
            if  record_date<= end and record_date >= start:
                json_data.append(d)
        conn.close()
        return json_data

if __name__ == '__main__':
    #get_hourly_data_from_csv('08NH005')
    hydro = CanHydrometrics(os.environ['SCRAP2_API_KEY'])
    # r = hydro.get_level('08NE074','2020-05-12','2020-05-12',result_type='history')
    r = hydro.get_historic('08NE074','2020-05-07','2020-05-14','LEVEL')
    print (r)


    