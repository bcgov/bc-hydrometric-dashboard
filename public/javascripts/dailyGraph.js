//load,parse and graph hourly discharge data
var rtData = { 
    data: [],
    get: function(){return this.data;},
    set: function(y){
        this.data = y;
        drawDailyGraph();
    }
 };

function buildDailyUrl(station, format='json'){
    var router = "./daily"
    var url = router + "?station=" + station + "&format=" + format;
    return url
}
function loadDailyJson(station){
    //get from url, parse dates, fix fields
    var url = buildDailyUrl(station);
    d3.json(url,function(data){
        //call back function loads data to window.rtData
        data.forEach(function(d){
            d["Date"] = d3.isoParse(d["Date"]);
            var myFormat = d3.timeFormat("%m-%d %H");
            for (var param in d){
                if (param != 'Date' && param != "Discharge / Débit (cms)"){
                    delete d[param];
                }
                if (param == "Discharge / Débit (cms)"){
                    d['Discharge'] = d["Discharge / Débit (cms)"]
                    delete d[param]
                }
            }
            // truncate time to Hour
            // is this needed?
            d["Date"] =d3.timeFormat("%Y-%m-%d %H")(d.Date);
            
            return d;
        })
        // rollup to get average discharge per hour
        var result = d3.nest()
            .key(function(d) {
                return d.Date;
            })
            .rollup(function(v) { return d3.mean(v, function(d) { return d.Discharge; }); })
            .entries(data);
        result.forEach(function(d){
            //fix result key value names after nest
            d.Date = d3.timeParse("%Y-%m-%d %H")(d.key);
            d.Discharge = d.value;
            delete d.key;
            delete d.value;
            return d;
        })
        //return result to app
        window.rtData.set(result);
    })
}
function drawDailyGraph(){
    var parseTime = d3.timeParse("%d-%m-%Y");
    var humanFormat = d3.timeFormat("%B, %e, - %H:%M");
    setTimeout(function(){
        c3.generate({
            bindto: '#dailyGraph',
            data:{
                json: rtData.get(),
                keys: {
                    x: 'Date',
                    value: ['Discharge']
                },
                type: 'spline',
                color: '#011f4b',
                names: {
                    value: 'Discharge(cms)',
                }            
            },
            point: {
                show: false
            },
            axis:{
                x:{
                    type: 'timeseries',
                    tick: {
                        format: '%B %e',
                        count: 30
                }
                }
            },
            tooltip: {
                format: {
                    title: function (d) { return 'Flow for: ' + humanFormat(d); },
                    value: function (value, ratio, id) {
                        var format = id === 'data1' ? d3.format(',') : d3.format('.1f');
                        return format(value) + ' m3/s';
                    }
                }
            }
        });
    },1000)

}

