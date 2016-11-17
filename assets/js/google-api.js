

var map;
var infoWindow;
var service;

function initialize() {
  var mapOptions = {
    zoom: 19,
    center: new google.maps.LatLng({{ restaurant_info.results[0].geometry.location.lat }}, {{ restaurant_info.results[0].geometry.location.lng }})
  };
  map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

  infoWindow = new google.maps.InfoWindow();
  var service = new google.maps.places.PlacesService(map);
  service.getDetails({
    placeId: '{{ restaurant_info.results[0].place_id }}'
  }, function(result, status) {
    if (status != google.maps.places.PlacesServiceStatus.OK) {
      alert(status);
      return;
    }
    var marker = new google.maps.Marker({
      map: map,
      position: result.geometry.location
    });
    var address = result.adr_address;
    var newAddr = address.split("</span>,");

    infoWindow.setContent(result.name + "<br>" + newAddr[0] + "<br>" + newAddr[1] + "<br>" + newAddr[2]);
    infoWindow.open(map, marker);
  });

}

google.maps.event.addDomListener(window, 'load', initialize);