var express = require('express');
var csv = require('csvtojson');
var request = require('request')
const sqlite3 = require('sqlite3').verbose();
var router = express.Router();

/* GET station info */
//gets daily and hourly csv --  combines into one file for realtime flow
// station, format, stats_type
router.get('/', function(req, res, next) {
  //http://localhost:3000/realtime?station=08NH005&format=json
  var station = req.query.station
  var type = req.query.format
  var resp
  console.log(req.query)

  if (type=='json'){
    getRealtime(station,function(d){
      console.log(d);
      res.send(d);
    });  
  }

  else{
    resp = 'Invalid type: ' + type;
    res.send(resp)
  }

});

function getCSV(url, callback){
  var dataset = [];
  csv()
    .fromStream(request.get(url))
    .on('json',(json)=>{
        // csvRow is an array
        dataset.push(json);
    })
    .on('done',(error)=>{
      callback(dataset);
    })
}
function getRealtime(station,callback){
  var dailyurl = 'http://dd.weather.gc.ca/hydrometric/csv/BC/daily/BC_'
  + station +'_daily_hydrometric.csv';
  var hourlyurl = 'http://dd.weather.gc.ca/hydrometric/csv/BC/hourly/BC_'
  + station +'_hourly_hydrometric.csv';
  getCSV(dailyurl,function(dj){
    var dailyJson = dj;
    var hourlyJson;
    getCSV(hourlyurl,function(hj){
      console.log(dailyJson);
      hourlyJson = hj;
      var firstHourlyDate = Date.parse(hourlyJson[0].Date);
      var cutIndex = 0;
      for (var i = dailyJson.length - 1; i >= 0; --i){
        //console.log(dailyJson[i].Date + " ------- " + hourlyJson[0].Date);
        if (Date.parse(dailyJson[i].Date)<= firstHourlyDate){
          cutIndex = i;
          break;
        }
      }
      dailyJson.splice(i,dailyJson.length-i-1);
      var nJson = dailyJson.concat(hourlyJson);
      callback(nJson);
    })
  })
}
module.exports = router;
