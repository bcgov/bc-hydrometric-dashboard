#current observations / forcasts for Canada weather stations
import math
import datetime
import requests
import csv
import xml.etree.ElementTree as ET
import sqlite3
conn = sqlite3.connect(':memory:')
data_root = 'http://dd.weatheroffice.ec.gc.ca/citypage_weather/xml/'
weather_stations = []

class Station:
    station_url = 'http://dd.meteo.gc.ca/observations/doc/'
    
    def __init__(self,station_cd,name,long, lat, province='BC',elevation=None, time_zone=None):
        self.long_lat = None
        self.elevation = None
        self.name = None
        self.province = None
        self.time_zone = None
    
class Stations:
    import sqlite3
    stationURL = 'http://dd.meteo.gc.ca/observations/doc/swob-xml_station_list.csv'
    
    def __init__(self,conn, province=None):
        self.conn = conn
        self.province = province
        conn.execute("DROP TABLE IF EXISTS stations")
        conn.execute("""CREATE TABLE stations(
            name text,
            station_id txt,
            province text,
            longitude real,
            latitude real,
            elevation real,
            time_zone text
        )
        """)
        self.stations = []
        r = requests.get(self.stationURL)
        if not r.ok:
            print('Failed to get data:', r.status_code)
        else:
            
            w = csv.reader(r.text.strip().split('\n'))

            station_list = []
            for r in w:
                if w.line_num==1:
                    header = r 
                else:
                    d = {}
                    i = 0 #index of field
                    for v in r:
                        f = header[i]
                        
                        if f in ['Latitude','Longitude','Elevation']:
                            try:
                                d[f]=float(v)
                            except:
                                d[f]=None
                        else:
                            d[f]=v
                        i += 1 #increment field index
                    if (d['Province']==self.province or self.province==None) and d['AUTO/MAN']=='Auto':
                        if len(d['# WMO'].strip())>0:
                            if d['EN name']== 'CLINTON RCS':
                                station_list.append(d)
                            else:
                                station_list.append(d)
            for s in station_list:
                if s['Latitude'] and s['Longitude']:
                    self.addStation(s['# WMO'],s['EN name'],s['Latitude'],s['Longitude'],s['Elevation'],s[' STD Time Zone / Fuseau horaire heure normale'])
                else:
                    station_list.remove(d)

    def addStation(self,station_cd,name,long, lat,elevation, time_zone):
        self.conn.execute("""INSERT INTO stations 
                        (name, station_id,province,longitude,latitude,elevation,time_zone)
                        VALUES (?,?,?,?,?,?,?)""",(name, station_cd,self.province,long,lat,elevation,time_zone))       
        print ("Station {} added".format(str(station_cd)))
        s = Station(station_cd,name,(long,lat),elevation,time_zone,self.province)
        self.stations.append(s)

    def addObservation(self,station_cd,observation_list):
        #add the table if it doesn't exist already
        #23 columns
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS observations(
                station_id text,
                time_utc text,
                mean_sea_level real, mean_sea_level_units text,
                tendency_amount real, tendency_amount_units text,
                tendency_characteristic text,
                horizontal_visibility real, horizontal_visibility_units text,
                air_temperature real, air_temperature_units text,
                dew_point real, dew_point_units,
                relative_humidity real, relative_humidity_units text,
                wind_speed real, wind_speed_units text,
                wind_direction text,
                wind_gust_speed real, wind_gust_speed_units text,
                total_cloud_cover real,
                wind_chill real,
                humidex real
            );
        """)
        for observation in observation_list:
            vHolder = ','.join(['?']*23)
            sql = f"INSERT INTO observations values({vHolder})"
            conn.execute(sql,observation)


def parse_hourly_xml(xmlstring):
    #parses weather station data to dictionary
    #example url http://dd.meteo.gc.ca/observations/xml/BC/hourly/hourly_bc_2019032016_e.xml
    '''
    observation_dict = {station:
                                {meta:
                                        {station_name:"",
                                        latitude:"",
                                        longitude:"",
                                        transport_canada_id:"",
                                        wmo_station_number:"",
                                        climate_station_number:""
                                        },
                                observations: [
                                    {time_utc:"",
                                    present_weather: 
                                                    {value:"",
                                                    unit:""}
                                    mean_sea_level:
                                                    {value:"",
                                                    unit:""}
                                    tendency_amount:
                                                    {value:"",
                                                    unit:""}
                                    tendency_characteristic:
                                                    {value:"",
                                                    unit:""}
                                    horizontal_visibility :
                                                    {value:"",
                                                    unit:""}
                                    air_temperature:
                                                    {value:"",
                                                    unit:""}
                                    dew_point:
                                                    {value:"",
                                                    unit:""}
                                    relative_humidity:
                                                    {value:"",
                                                    unit:""}
                                    wind_speed:
                                                    {value:"",
                                                    unit:""}
                                    wind_direction:
                                                    {value:"",
                                                    unit:""}
                                    wind_gust_speed:
                                                    {value:"",
                                                    unit:""}
                                    total_cloud_cover:
                                                    {value:"",
                                                    unit:""}
                                    wind_chill:
                                                    {value:"",
                                                    unit:""}
                                    humidex:
                                                    {value:"",
                                                    unit:""}
                                    }
                                ]
                                }
                        }

    '''
    xml_root = ET.fromstring(xmlstring)
    station = xml_root[1][0][0][0][1][0]
    i = 0
    observations = {}
    for member in xml_root:
        if i > 0:
            station = None
            obs_meta = {}
            i_elements = member[0][0][0][1] #observations/metadata/set/identification-elements
            time = {}
            station_meta = {}

            for e in i_elements:
                d = e.attrib
                if 'observation_date_utc' == d['name']:
                    obs_meta['time_utc'] = d['value']
                elif 'observation_date_local_time' == d['name']:
                    obs_meta['time_local'] = d['value']
                else:
                    station_meta[d['name']] = {'units':d['uom'],'value':d['value']}
                    if 'climate_station_number' in d.values():
                        station = d['value']
            result = member[0][6][0]
            for r in result:
                #print (r.attrib)
                d = r.attrib
                obs_meta[d['name']] = {'units':d['uom'],'value':d['value']}
            
            observations[station] = {'meta':station_meta, 'weather':obs_meta}       
        i+=1
    return observations

def download_precipitation(station, number_of_days):
    #ref ftp://ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Readme.txt
    pass
    #http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=1706&Year=${year}&Month=${month}&Day=14&timeframe=1&submit= Download+Data

    


def download_observations(province,number_of_hours=0, number_of_days=0):
    #manages get requests
    url = 'https://dd.meteo.gc.ca/observations/xml/{}/hourly/'.format(province.upper())

    #first time step to get data for    
    d1 = datetime.datetime.utcnow() - datetime.timedelta(days=number_of_days,hours=number_of_hours)

    #timestep hours between now and number of days to download
    total_hrs = math.floor((datetime.datetime.utcnow() - d1).total_seconds() / 3600)
    observation_dict = {}
    for h in range(total_hrs):
        dh = d1 + datetime.timedelta(hours=h)
        date = dh.strftime('%Y%m%d%H')
        #hour = datetime.datetime.now().time().strftime('%H')
        file = 'hourly_{}_{}_e.xml'.format(province.lower(),date)
        xml_url = url + file

        with requests.Session() as s:
            try:
                print ("Connecting to {}".format(xml_url))
                r = s.get(xml_url, timeout = 2.0)
            except TimeoutError:
                print ("Response timeout: {}".format(xml_url))
            except ConnectionError:
                print ("Connection error to: {}".format(xml_url))
            observation_dict.update(parse_hourly_xml(r.content))
            print (len(observation_dict))
    return observation_dict
#s = Stations(conn,'BC')
#print (len(s.stations))
obs = download_observations(province = 'BC', number_of_hours=0, number_of_days=1)
print ('done')


