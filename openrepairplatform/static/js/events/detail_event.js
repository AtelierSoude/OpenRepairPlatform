let event_map = L.map('event_map').setView([latitude, longitude], 16);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    minZoom: 12,
    maxZoom: 99,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoiYXRlbGllcnNvdWRlIiwiYSI6ImNqazEwZW16aDAzbDkza254cHhucHJtMncifQ.01v1DWXApDJmCySy4QvD4A',
    noWrap: true,
    reuseTiles: true,
}).addTo(event_map);
L.marker([latitude,longitude]).addTo(event_map);
