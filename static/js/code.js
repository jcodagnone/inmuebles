// inicializa la aplicacion
function load() {
  gApp = new AlquilerMap('map');


  //document.getElementById('stop').onclick = function () {
  //  gApp.gMode = 'stop';
  //}
}


////////////////////////////////////////////////////////////////////////////
// Clase que maneja la aplicacion
///////////////////////////////////////////////////////////////////////////
function AlquilerMap(mapId) {
  if (GBrowserIsCompatible()) {
    this.gMode = "start";
    this.map = this.load(mapId);

    //this.map.setMapType(G_SATELLITE_MAP);
    this.buildCustomMap();
    
    var ptr = this;
    /*GEvent.addListener(this.map, "click", function(overlay, point) {
     *   if(ptr.gMode == "start") {
     *       ptr.gStart = point;
     *   } else if(ptr.gMode == "stop") {
     *       ptr.gStop = point;
     *   }
     *   ptr.dibujarStartStop();
     * }
     *
     * );
     */
  } else {
    alert('navegador incompatible');
  }
}

AlquilerMap.prototype.customTileBaseURL = 'http://flof.com.ar';

// el siguiente codigo tiene que estar en una funcion aislada, sino no anda
function createMarker(p, icon) {
    var marker = new GMarker(new GLatLng(p[4], p[3]), icon);
    marker.idApp = p[0];
    marker.provider   = p[1];
    marker.providerId = p[2];
    marker.textToRender = '';

    GEvent.addListener(marker, "click", function() {
        if(marker.textToRender == '') {
           GDownloadUrl('/map/data/' + marker.provider + '/' 
                         + marker.providerId + '/info/',
             function(data, responseCode) {
                if(responseCode == 200) {
                    marker.textToRender = data;
                    marker.openInfoWindowHtml(marker.textToRender);
                }
             });
        } else {
            marker.openInfoWindowHtml(marker.textToRender);
        }
   });
   return marker;
}

function createIcon(color) {
    var icon = new GIcon();
    icon.image = 'http://maps.google.com/mapfiles/ms/icons/' + color + '-dot.png'
    icon.iconSize = new GSize(32, 32);
    icon.shadowSize = new GSize(32, 32);
    icon.iconAnchor = new GPoint(9, 34);
    icon.infoWindowAnchor = new GPoint(18, 25);
    return icon;
}

AlquilerMap.prototype.load = function(/*String*/ mapId) {
    var map = new GMap2(document.getElementById(mapId));
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());
    new GKeyboardHandler(map);
    map.setCenter(new GLatLng(-34.61, -58.428382873535156), 15);
    var zoom = map.getBoundsZoomLevel(gInitBound);
    map.setCenter(gInitBound.getCenter(), zoom);

    var icons = new Object();
    icons['IMPORTADO'] = createIcon('yellow');
    icons['POSIBLE'] = createIcon('green');
    icons['NO DISPONIBLE'] = createIcon('red');

   var mgr = new GMarkerManager(map);
    for(i in gSpotPoints) {
        var marker = createMarker(gSpotPoints[i], icons[gSpotPoints[i][5]])
        mgr.addMarker(marker, 0);
    }
    mgr.refresh();
    return map;
}

// esto viene de flof....solo lo pueden usar personas con permiso
// http://flof.com.ar/info/terms/
AlquilerMap.prototype.buildCustomMap = function() {
    var map = this.map;
    for(var i = 0; i < G_DEFAULT_MAP_TYPES.length; i++) {
        map.removeMapType(G_DEFAULT_MAP_TYPES[i]);
    }
    var copyrightCollection = new GCopyrightCollection("Calles");
    var copyright = new GCopyright(1342,
                        new GLatLngBounds(
                        new GLatLng(-36.1587715148926, -62.992603302002), 
                        new GLatLng(-34.5340881347656, -58.3418045043945)),
                        6,
                         "<a style='color: #ffffff;' "
                        + "href='/info/terms/#otros_servicios'>: De donde "
                        + "vienen los dibujos de calles y ciudades?</a>");
    copyrightCollection.addCopyright(copyright);
    var tileCountry= new GTileLayer(copyrightCollection, 6, 17);
    ptr = this;
    tileCountry.getTileUrl=function(a,b,c) {
        // en google map v2 el 17 - b cambia por b.
        return  ptr.customTileBaseURL + '/bin/map/streets/?y=' + a.y + 
               '&x=' + a.x + '&zoom=' + (17 - b);
    }
    tileCountry.isPng = function() { return true };
    var layer=[G_SATELLITE_MAP.getTileLayers()[0],
               G_HYBRID_MAP.getTileLayers()[1],
               tileCountry];
    var custommap = new GMapType(layer, G_SATELLITE_MAP.getProjection(), 
                                 "Calles", G_SATELLITE_MAP);
    map.addMapType(custommap);
    map.setMapType(custommap);
}


