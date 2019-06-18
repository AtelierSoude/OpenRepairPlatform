function htmlEscape(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\//g, '&#x2F;');
}

function popup_message(place){
    message = "<a href=\"" + place.get_absolute_url + "\">" ;
    if (place.picture) {
        message += "<img src=\"" + place.picture + "\" class=\"pt-2 pb-2 w-100\">";
    }
    message += htmlEscape(place.name) + "</a> - ";
    message += htmlEscape(place.category);
    message += "<br> <a href=\"" + place.orga_url + "\">" + htmlEscape(place.orga_name) + "</a> - ";
    message += htmlEscape(place.address);
    message += "<hr class='mt-2 mb-2'>" + place.description;
    return message;
}

var blueMarker = L.AwesomeMarkers.icon({
    prefix: 'fa',
    icon: 'home',
    markerColor: 'darkblue'
});

var place_map = L.map('place_map').setView([45.76, 4.84], 14);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 7,
    maxZoom: 999,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoiYXRlbGllcnNvdWRlIiwiYSI6ImNqazEwZW16aDAzbDkza254cHhucHJtMncifQ.01v1DWXApDJmCySy4QvD4A',
    noWrap: true,
    reuseTiles: true,
}).addTo(place_map);

fetch('/api/location/place-list/')
    .then(function(res){ return res.json(); })
    .then(function(places){
        places.forEach(function(place){
            let marker = L.marker([place.latitude, place.longitude], {icon: blueMarker}).addTo(place_map);
            marker.bindPopup(popup_message(place));
        });
    });
