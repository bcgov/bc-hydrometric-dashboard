//load,parse and graph historic daily discharge data

var hUrl = "./historic?station=08NH005&format=json"

var hData = { 
    data: [],
    get: function(){return this.data;},
    set: function(y){
        this.data = y;
        drawHistoricGraph();
    }
 };

//build url by station
function buildHistoricUrl(station, format='json'){
    var router = "./historic"
    var url = router + "?station=" + station + "&format=" + format;
    return url
}

//Build JSON from response
function loadHistoricJson(station){
    var url = buildHistoricUrl(station);
    var parseTime = d3.timeParse("%d-%m-%Y");
    $.getJSON(url,function(d){
        //add date from year month day
        $.each(d, function(row, c){
            var myDate = c["DAY"] + "-" + c["MONTH"] + "-" + "2018"
            //d["Date"] = d3.isoParse(d["Date"]);
            var myFormat = d3.timeFormat("%Y-%m-%d");
            c["Date"] = parseTime(myDate);
            delete c.DAY;
            delete c.MONTH;
            delete c.STATION_NUMBER;
            //d["Date"] = myFormat(parseTime(myDate));
            return c;
        });
        hData.set(json2array(d));
    });
}

function json2array(jsonObj){
    //build data array from json --- fields are in first array
    var darray = [];
    $.each(jsonObj, function(fprop,val){
      var fieldList = [];
      var adata = [];
      $.each(val,function(field,value){
        if (fieldList.indexOf(field) == -1){
          fieldList.push(field);
        }
        adata.push(value);
      })
      if (darray.length == 0){
        darray.push(fieldList);
      }
      if (adata.length != 0){
        darray.push(adata);
      }
    });
    return darray;
  }

function drawHistoricGraph(){
    var parseTime = d3.timeParse(("%Y-%m-%d %H"));
    var humanFormat = d3.timeFormat("%B, %e");
    //build chart
    window.chart = c3.generate({
            bindto: '#myGraph',
            data:{
                rows: hData.get(),
                x: 'Date',
                type: 'area-spline',
                names: {
                    min: 'Min',
                    PCT25: '25th %ile',
                    PCT50: 'Median',
                    PCT75: '75th %ile',
                    max: 'Max'
                },
                colors: {
                    min: '#08519c',
                    PCT25: '#3182bd',
                    PCT50: '#6baed6',
                    PCT75: '#9ecae1',
                    max: '#969696'
                }
            
            },
            point: {
                show: false
            },
            axis:{
                x:{
                    type: 'timeseries',
                    tick: {
                        count: 12,
                        format: '%B',
                        fit: true
                }
                }
            },
            grid: {
                x: {
                    show: true
                },
                y: {
                    show: true
                }
            },
            tooltip: {
                format: {
                    title: function (d) { return 'Flow for: ' + humanFormat(d); },
                    value: function (value, ratio, id) {
                        var format = id === 'data1' ? d3.format(',') : d3.format('.1f');
                        return format(value) + ' m3/s';
                    }
        //            value: d3.format(',') // apply this format to both y and y2
                }
            }
            // ,
            // subchart: {
            //     show: true
            // }

        });
        setTimeout(window.chart.load({
            rows: window.dData
        }),1000);
    

    
}