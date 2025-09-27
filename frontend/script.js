let map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Add geocoder control for searching countries/locations
L.Control.geocoder({
    defaultMarkGeocode: false
}).on('markgeocode', function(e) {
    const { center, name } = e.geocode;
    map.setView(center, 5); // Zoom to country level to show labels
    L.marker(center).addTo(map).bindPopup(name).openPopup();
}).addTo(map);

let marker;

map.on('click', function(e) {
    if (marker) map.removeLayer(marker);
    marker = L.marker(e.latlng).addTo(map);
});

// Populate days based on month
document.getElementById('month').addEventListener('change', function() {
    const month = this.value;
    const daySelect = document.getElementById('day');
    daySelect.innerHTML = '<option value="">Select Day</option>';
    if (month) {
        const daysInMonth = new Date(2024, month, 0).getDate(); // Use leap year for Feb max
        for (let i = 1; i <= daysInMonth; i++) {
            const day = i < 10 ? '0' + i : i;
            daySelect.innerHTML += `<option value="${day}">${day}</option>`;
        }
    }
});

// Select all conditions button
document.getElementById('select-all').addEventListener('click', function() {
    const options = document.getElementById('conditions').options;
    for (let i = 0; i < options.length; i++) {
        options[i].selected = true;
    }
});

document.getElementById('query-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!marker) return alert('Please select a location on the map.');

    const lat = marker.getLatLng().lat;
    const lon = marker.getLatLng().lng;
    const month = document.getElementById('month').value;
    const day = document.getElementById('day').value;
    const day_of_year = `${month}-${day}`;
    const selectedConditions = Array.from(document.getElementById('conditions').selectedOptions).map(opt => opt.value);

    // Map conditions to backend format (convert thresholds to metric)
    const conditions = {};
    if (selectedConditions.includes('very_hot')) conditions.very_hot = {param: 'T2M_MAX', threshold: 32.22, operator: '>'};  // 90°F to °C
    if (selectedConditions.includes('very_cold')) conditions.very_cold = {param: 'T2M_MIN', threshold: 0, operator: '<'};    // 32°F to °C
    if (selectedConditions.includes('very_windy')) conditions.very_windy = {param: 'WS10M', threshold: 8.94, operator: '>'}; // 20 mph to m/s
    if (selectedConditions.includes('very_wet')) conditions.very_wet = {param: 'PRECTOT', threshold: 12.7, operator: '>'};   // 0.5 in to mm

    try {
        const response = await fetch('http://127.0.0.1:5000/api/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({lat, lon, day_of_year, conditions})
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        let resultsHtml = '<h2>Results:</h2>';
        for (const [cond, res] of Object.entries(data.results)) {
            resultsHtml += `<p>${cond}: ${res.probability}% likelihood (Mean: ${res.mean.toFixed(2)} ${res.metadata.units})</p>`;
        }
        resultsHtml += '<button onclick="downloadCsv()">Download CSV</button>';

        document.getElementById('results').innerHTML = resultsHtml;
        window.csvData = data.csv_data;  // Store for download
    } catch (error) {
        document.getElementById('results').innerHTML = `<h2>Error:</h2><p>${error.message}</p>`;
        console.error('Query error:', error);
    }
});

function downloadCsv() {
    const blob = new Blob([window.csvData], {type: 'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'weather_data.csv';
    a.click();
}