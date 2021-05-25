let event_map = L.map('event_map').setView([latitude, longitude], 16);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 12,
    maxZoom: 99,
    id: 'mapbox/streets-v11',
    accessToken: 'pk.eyJ1IjoiY2xlbWVudGFzIiwiYSI6ImNraWRqdHoxYjBzcDYyeG81cDdjaml6b3YifQ.KeSzBsJGsceaxeNuqq66hw',
    noWrap: true,
    reuseTiles: true,
}).addTo(event_map);
L.marker([latitude,longitude]).addTo(event_map);

event_map.scrollWheelZoom.disable();
