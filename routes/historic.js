var express = require('express');
var csv = require('csvtojson');
var request = require('request')
const sqlite3 = require('sqlite3').verbose();
var router = express.Router();

/* GET station info */
// station, format, stats_type
router.get('/', function(req, res, next) {
  //http://localhost:3000/historic?station=08NH005&format=json
  var station = req.query.station
  var type = req.query.format

  if (type=='json'){
    var sql = "SELECT STATION_NUMBER,MONTH,DAY,MIN,MAX,PCT25,PCT50,PCT75 FROM STATION_STATS WHERE STATION_NUMBER ='" 
    + station + "';";
    console.log('sql: '+sql)
      // open the database
    var db = new sqlite3.Database('./BC_Hydat.sqlite3', sqlite3.OPEN_READWRITE, (err) => {
      if (err) {
        console.error(err.message);
      }
      console.log('Connected to the sql database.');
    });

    db.all(sql, [], (err, rows) => {
      if (err) {
        throw err;
      }
      dataJSON = []
      rows.forEach((row) => {
        dataJSON.push(row);
      });
      res.send(dataJSON)
    });

    // close the database connection
    db.close();
    console.log('Database connection closed')
  }
  else{
    res.send('Invalid type: ' + type);
  }
});

module.exports = router;
