let placeMap = L.map('place_map').setView([30.76, 4.84], 14);
placeMap.scrollWheelZoom.disable();

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 7,
    maxZoom: 16,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoiYXRlbGllcnNvdWRlIiwiYSI6ImNqazEwZW16aDAzbDkza254cHhucHJtMncifQ.01v1DWXApDJmCySy4QvD4A',
    noWrap: true,
    reuseTiles: true,
}).addTo(placeMap);

L.marker([latitude, longitude]).addTo(placeMap).bindPopup(placeName).openPopup();
