# flask app for rest api and webmap
import os
from flask import Flask,render_template
from flask_restful import Resource, Api
from datetime import datetime,timedelta
from bchyrometric import CanHydrometrics
app = Flask(__name__)
#app._static_folder = 'static'
api = Api(app)

class dailyflow(Resource):
    def __init__(self):
        self.hydro = CanHydrometrics(os.environ['SCRAP2_API_KEY'])
    def get(self,station_id):
        stop = datetime.today().strftime('%Y-%m-%d')
        start = datetime.today() - timedelta(days=1)
        start = start.strftime('%Y-%m-%d')
        r = self.hydro.get_flow(station_id,start,stop,result_type='history')
        return r
    def put(self,station_id):
        stop = datetime.today().strftime('%Y-%m-%d')
        start = datetime.today() - timedelta(days=1)
        start = start.strftime('%Y-%m-%d')
        r = self.hydro.get_flow(station_id,start,stop,result_type='history')
        return r
class weeklyflow(Resource):
    def __init__(self):
        self.hydro = CanHydrometrics(os.environ['SCRAP2_API_KEY'])
    def get(self,station_id):
        stop = datetime.today().strftime('%Y-%m-%d')
        start = datetime.today() - timedelta(days=7)
        start = start.strftime('%Y-%m-%d')
        r = self.hydro.get_flow(station_id,start,stop,result_type='history')
        return r
    def put(self,station_id):
        stop = datetime.today().strftime('%Y-%m-%d')
        start = datetime.today() - timedelta(days=7)
        start = start.strftime('%Y-%m-%d')
        r = self.hydro.get_flow(station_id,start,stop,result_type='history')
        return r
class historicflow(Resource):
    def get(self,station_id):
        return f'get {station_id}'
    def put(self,station_id):
        return f'put {station_id}'



api.add_resource(dailyflow,'/dailyflow/<string:station_id>')
api.add_resource(weeklyflow,'/weeklyflow/<string:station_id>')

@app.route("/map")
def index_router():
    return render_template('index.html',title='BC-Hydrometric-Dashboard')#,mapId='map', historicGraph='myGraph',dailyGraph='dailyGraph')

if __name__ == '__main__':
    app.run(debug=True)
