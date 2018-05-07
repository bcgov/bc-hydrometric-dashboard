var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'BC-Hydrometric-Dashboard',mapId:'map', historicGraph: 'myGraph',dailyGraph:'dailyGraph' });
});

module.exports = router;
