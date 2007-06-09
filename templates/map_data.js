$def with (points, sw, ne)
gSpotPoints = $points;
gInitBound = new GLatLngBounds(new GLatLng($sw[1], $sw[0]),
                               new GLatLng($ne[1], $ne[0]));

