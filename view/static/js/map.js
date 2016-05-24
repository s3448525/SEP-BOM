var map, searchBox, geocoder;
var locations = [];
// var locations = [];
// Google maps initialiser
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 8,
        mapTypeControlOptions: { mapTypeIds: [] },
        streetViewControl: false,
        zoomControl: false,
    });

    searchBox = new google.maps.places.SearchBox(document.getElementById('search-box'));

    // Create the search box and link it to the UI element.
    var input = document.getElementById('search-box');
    var searchBox = new google.maps.places.SearchBox(input);

    // Bias the SearchBox results towards current map's viewport.
    map.addListener('bounds_changed', function() {
        searchBox.setBounds(map.getBounds());
    });

    var markers = [];
    // Listen for the event fired when the user selects a prediction and retrieve
    // more details for that place.
    searchBox.addListener('places_changed', function() {
        var places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }

        // Save location coordinates for later use
        document.getElementById('location-coord-box').value =
            places[0].geometry.location.lat() + "," + places[0].geometry.location.lng();

        // Clear out the old markers.
        markers.forEach(function(marker) {
            marker.setMap(null);
        });
        markers = [];

        // For each place, get the icon, name and location.
        var bounds = new google.maps.LatLngBounds();
        places.forEach(function(place) {
            // Create a marker for each place.
            markers.push(new google.maps.Marker({
                map: map,
                title: place.name,
                position: place.geometry.location
            }));

            if (place.geometry.viewport) {
                // Only geocodes have viewport.
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        map.fitBounds(bounds);
        app.search();
    });

    // Listen to bound change
    google.maps.event.addListener(map, 'bounds_changed', function() {
        var bounds =  map.getBounds(),
            ne = bounds.getNorthEast(),
            sw = bounds.getSouthWest(),
            center = bounds.getCenter();
        // Get bound size
        var r = 6371008,
            lat1 = center.lat() / 57.2958,
            lon1 = center.lng() / 57.2958,
            lat2 = ne.lat() / 57.2958,
            lon2 = ne.lng() / 57.2958,
            dis = r * Math.acos(Math.sin(lat1) * Math.sin(lat2) + Math.cos(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1));
        // Set search radius
        document.getElementById('search-radius').value = parseInt(dis);
        app.getObservations(center.lat(), center.lng(), parseInt(dis));
    });

    // Focus to users location
    //setUserLocation();
    map.panTo(new google.maps.LatLng(-37.8095,144.964));
    // Display observation points
    // addMarkers(map, locations);
}

// Get user's location
function setUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Focus map to user's location
function showPosition(position) {
    var lat = position.coords.latitude;
    var lng = position.coords.longitude;
    map.setCenter(new google.maps.LatLng(lat, lng));
}

// Load all forecast/observation location points into an array and load to map
function addMarkers(map, location_array) {
    deleteMarkers();
    for (var i = 0; i < location_array.length; i++) {
        var loc = location_array[i];
        // console.log(loc);
        var redCircle ={
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: 'red',
            fillOpacity: .5,
            scale: 4.5,
            strokeColor: 'white',
            strokeWeight: 1
        };
        var marker = new google.maps.Marker({
            position: {lat: loc[1], lng: loc[2]},
            icon: redCircle,
            map: map,
            title: loc[0],
            // zoom: 10,
        });
        locations.push(marker);
    }
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
    for (var i = 0; i < locations.length; i++) {
        locations[i].setMap(map);
    }
}

// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
    setMapOnAll(null);
}

// Shows any markers currently in the array.
function showMarkers() {
    setMapOnAll(map);
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
    clearMarkers();
    locations = [];
}

// Get current bound size
function getBoundSize() {
    var bounds = map.getBounds();
    console.log(bounds);
    var center = bounds.getCenter();
    var ne = bounds.getNorthEast();
    var r = 6371008;
    var lat1 = center.lat() / 57.2958;
    var lon1 = center.lng() / 57.2958;
    var lat2 = ne.lat() / 57.2958;
    var lon2 = ne.lng() / 57.2958;
    var dis = r * Math.acos(Math.sin(lat1) * Math.sin(lat2) + Math.cos(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1));
    console.log(dis);
    return dis;
}
