
$(document).ready(function(){
  $(".graph").hide()
  stationJson.set('WHSE_ENVIRONMENTAL_MONITORING.ENVCAN_HYDROMETRIC_STN_SP',
      ['STATION_NUMBER','STATION_NAME','WATERSHED_GROUP_CODE','WATERSHED_ID'
      ,'STATION_OPERATING_STATUS','REALTIME_URL','GEOMETRY'],
      'https://openmaps.gov.bc.ca/geo/pub/WHSE_ENVIRONMENTAL_MONITORING.ENVCAN_HYDROMETRIC_STN_SP/ows',
      "STATION_OPERATING_STATUS='ACTIVE-REALTIME'"
      );
  //need to load https://openmaps.gov.bc.ca/geo/pub/WHSE_ENVIRONMENTAL_MONITORING.ENVCAN_HYDROMETRIC_STN_SP/ows?service=WMS&request=GetCapabilities
  // add to map with popup... popup should have link for graphs
  // draw graphs with loadDailyJson(station) or loadHistoricJson(station)... this will also trigger graph redraw
});
// stationJson.set('WHSE_ENVIRONMENTAL_MONITORING.ENVCAN_HYDROMETRIC_STN_SP',
//   ['STATION_NUMBER','STATION_NAME','WATERSHED_GROUP_CODE','WATERSHED_ID','STATION_OPERATING_STATUS'],
//   'https://openmaps.gov.bc.ca/geo/pub/WHSE_ENVIRONMENTAL_MONITORING.ENVCAN_HYDROMETRIC_STN_SP/ows'
// );

function drawMap(){
    //basic map
  var map = L.map('map').setView([51, -123.667], 10);
  //L.esri.basemapLayer("Topographic").addTo(map);
  var URL_BCBASE = "http://maps.gov.bc.ca/arcserver/services/Province/web_mercator_cache/MapServer/WMSServer"
  wmsBCBASELayer = L.tileLayer.wms(URL_BCBASE,{
    format:'image/png',
    layers: '0',
    transparent: 'false'
  });
  map.addLayer(wmsBCBASELayer);
  //load data
  var sdata = stationJson.get();

  function stationPopup(e) {

    var layer = e.target;
    var station = layer.feature;
    $(".graph").fadeOut(1000)
    loadDailyJson(station.properties.STATION_NUMBER);
    loadHistoricJson(station.properties.STATION_NUMBER);
    $(".graph").fadeIn(500);

    if (station) {
      var latlng = [station.geometry.coordinates[1], station.geometry.coordinates[0]];
  
      /*-----L.popup-----*/
      var popup = L.popup({
        offset: [0, 0],
        closeButton: true
    });
      popup.setLatLng(latlng);
      var strContent = "<h6>Station Number: "+ station.properties.STATION_NUMBER + 
        "</b><h6>Name: "+ station.properties.STATION_NAME + 
        "</b><h6>Watershed Group: "+ station.properties.WATERSHED_GROUP_CODE+ 
        "</b><h6>Watershed ID: "+ station.properties.WATERSHED_ID + 
        "</b><h6>Status: "+ station.properties.STATION_OPERATING_STATUS;
        if(station.properties.REALTIME_URL != null){
          strContent += "<br><br><a href='" 
          + station.properties.REALTIME_URL 
          + "' target='_blank' style='font-size:2em'>Real Time Data</a>";
          
        } 
      popup.setContent(strContent);
      popup.addTo(map);
    }
  }
  var stationLyr = L.geoJSON(sdata, {
    onEachFeature: function(feature, layer) {
      layer.on({
        click: stationPopup
      })
    },
    pointToLayer: function(feature,latlng){
      label = String(feature.properties.STATION_NUMBER);
      return new L.CircleMarker(latlng, {
        radius: 4,
      }).bindTooltip(label, {permanent: true, opacity: 0.7});
      }
    });
    lyrStations = L.geoJSON(sdata,{
        onEachFeature: function(feature, layer) {
          layer.on({
            click: stationPopup
          })
        },
        //call function to set point style options
         pointToLayer: function (feature, latlng){
          var att = feature.properties;
          var clr;
          if (att.STATION_OPERATING_STATUS == 'ACTIVE'||att.STATION_OPERATING_STATUS == 'ACTIVE-REALTIME'){
            clr = 'rgb(189, 41, 41)'
            var markerOptions = {radius:6, color:clr, fillColor:clr, fillOpacity:0.8};
            var marker = L.circleMarker(latlng, markerOptions);
  
            return marker;
            };
          }
      });
  stationLyr.addTo(map);
  
}

var stationJson = {
  name: null,
  fields: null,
  data: null,
  url:null,
  CQLfilter:null,
  callback: function(response){
    this.data= response;
    window.drawMap();
  },
  callbackName: 'stationJson.callback',
  get: function(){return this.data},
  set: function(name, fields=null,url=null,cqlFilter=null){
    this.name = name;
    //field names ['name1','name2']
    this.fields = fields;
    this.url= url;
    this.CQLfilter = cqlFilter;
  
    if (name!=null && url!=null){
      getWFSjson(this.url, this.name, this.fields, this.callbackName, this.CQLfilter);
    }
    else {console.log('wfs connection requires source name and url');}
  }
}
//fetch WFS (json) from openmaps geoserver
function getWFSjson(wfsURL, wfsTypeName, wfsProperties, wfsCallback, wfsCQLfilter,
  wfsBbox= "-139.1782824917356, 47.60393449638617, -110.35337939457779, 60.593907018763396, 'epsg:4326'",
  wfsGeometryProperty='GEOMETRY'){
  //case wfsCQLfilter is null
  var cqlString = (function(){
    if (wfsCQLfilter==null){
      return "bbox(" + wfsGeometryProperty + "," + wfsBbox + ")"
    }
    else {return "bbox(" + wfsGeometryProperty + "," + wfsBbox + ") AND " + wfsCQLfilter}
  })();
  
  var defaultParameters = {
    service: 'WFS',
    version: '2.0',
    request: 'GetFeature',
    typeName: wfsTypeName,
    outputFormat: 'text/javascript', //or application/json (but won't work w/ ajax dataType=jsonp )
    format_options: 'callback:' + wfsCallback,
    SrsName: 'EPSG:4326',
    propertyName: wfsProperties,
    cql_filter: cqlString
  };

  var parameters = L.Util.extend(defaultParameters);
  var URL = wfsURL + L.Util.getParamString(parameters);

  var ajax = $.ajax({
    url: URL,
    dataType: 'jsonp',
    jsonpCallback: wfsCallback,
    success: function(response) {
      console.log('executed wfs request');
      //map.spin(false);
    }
  });
}

