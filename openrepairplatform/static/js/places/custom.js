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
    message = "<h5><u><a href=\"" + place.get_absolute_url + "\">" ;
    message += htmlEscape(place.name) + "</a></u></h5> <br> ";
    message += "<h6>" + htmlEscape(place.address) + "</h6>";
    message += place.future_events + " événéments à venir";
    return message;
}

var place_map = L.map('place_map').setView([45.76, 4.84], 12);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}',{
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 7,
    maxZoom: 999,
    id: 'mapbox/streets-v11',
    accessToken: 'pk.eyJ1IjoiY2xlbWVudGFzIiwiYSI6ImNraWRqdHoxYjBzcDYyeG81cDdjaml6b3YifQ.KeSzBsJGsceaxeNuqq66hw',
    noWrap: true,
    reuseTiles: true,
}).addTo(place_map);

fetch('/api/location/place-list/')
    .then(function(res){ return res.json(); })
    .then(function(places){
        places.forEach(function(place){
            index = 0 
            if (place.future_events) {
                var blueMarker = L.AwesomeMarkers.icon({
                    prefix: 'fa',
                    icon: 'home',
                    markerColor: 'darkblue',
                    myCustomId: place.pk,
                });
                let marker = L.marker([place.latitude, place.longitude], {icon: blueMarker, myCustomId: place.pk}).addTo(place_map);
                marker.bindPopup(popup_message(place));
                if (index==0) {
                    marker.openPopup()
                }
                index+=1
            }
        });
    });
