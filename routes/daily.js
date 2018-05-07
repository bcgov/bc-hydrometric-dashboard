var express = require('express');
var csv = require('csvtojson');
var request = require('request')
const sqlite3 = require('sqlite3').verbose();
var router = express.Router();

/* GET station info */
// station, format, stats_type
router.get('/', function(req, res, next) {
  //http://localhost:3000/daily?station=08NH005&format=json
  var station = req.query.station
  var type = req.query.format
  var resp
  console.log(req.query)

  if (type=='json'){
    //case json daily
    var dataurl = 'http://dd.weather.gc.ca/hydrometric/csv/BC/daily/BC_'
    + station +'_daily_hydrometric.csv';
    console.log(dataurl);

    var dataset = [];
    csv()
      .fromStream(request.get(dataurl))
      .on('json',(json)=>{
          // csvRow is an array
          dataset.push(json);
      })
      .on('done',(error)=>{
        res.send(dataset);
      })
  }

  else{
    resp = 'Invalid type: ' + type;
    res.send(resp)
  }

});

module.exports = router;
