let placeMap = L.map('place_map').setView([30.76, 4.84], 14);
placeMap.scrollWheelZoom.disable();

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 7,
    maxZoom: 16,
    id: 'mapbox/streets-v11',
    accessToken: 'pk.eyJ1IjoiY2xlbWVudGFzIiwiYSI6ImNraWRqdHoxYjBzcDYyeG81cDdjaml6b3YifQ.KeSzBsJGsceaxeNuqq66hw',
    noWrap: true,
    reuseTiles: true,
}).addTo(placeMap);

L.marker([latitude, longitude]).addTo(placeMap).bindPopup(placeName).openPopup();
