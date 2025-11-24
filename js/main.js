// Yo! Lokalmedien Dashboard - Hauptlogik

// Globale Variablen
let map = null;
let markers = [];
let comparisonChart = null;
let currentSortColumn = 'score';
let currentSortOrder = 'desc';

// Gewichtungen (anpassbar)
let weights = {
    medien: 0.30,
    zielgruppe: 0.25,
    digital: 0.20,
    wirtschaft: 0.10,
    identitaet: 0.10,
    praktikabilitaet: 0.05
};

// ==========================================
// Initialisierung
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard wird initialisiert...');
    
    // Hauptfunktionen initialisieren
    updateRankingTable();
    updateSegmentAnalysis();
    setupComparisonSelects();
    updateWeightDisplay();
    updateAvgScore();
    
    // Statistiken aktualisieren
    document.getElementById('cityCount').textContent = cities.length;
    
    // Tab-Navigation Setup
    setupTabNavigation();
    
    // Filter-Events Setup
    setupFilterEvents();
    
    // Modal-Events
    setupModalEvents();
});

// ==========================================
// Tab Navigation
// ==========================================

function setupTabNavigation() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            // Alle Tabs und Contents deaktivieren
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Aktuellen Tab aktivieren
            this.classList.add('active');
            document.getElementById(this.dataset.tab + '-tab').classList.add('active');
            
            // Map initialisieren wenn Tab geöffnet wird
            if (this.dataset.tab === 'map' && !map) {
                setTimeout(() => {
                    initializeMap();
                }, 100);
            }
        });
    });
}

// ==========================================
// Filter Events
// ==========================================

function setupFilterEvents() {
    // Ranking Filter
    document.getElementById('searchFilter').addEventListener('input', updateRankingTable);
    document.getElementById('bundeslandFilter').addEventListener('change', updateRankingTable);
    document.getElementById('verlagFilter').addEventListener('change', updateRankingTable);
    document.getElementById('sortBy').addEventListener('change', updateRankingTable);
    
    // Map Filter
    document.getElementById('minScoreFilter').addEventListener('input', function() {
        document.getElementById('minScoreValue').textContent = this.value;
        updateMapMarkers();
    });
    document.getElementById('minKaufkraft').addEventListener('input', updateMapMarkers);
    document.getElementById('sizeFilter').addEventListener('change', updateMapMarkers);
    document.getElementById('mapVerlagFilter').addEventListener('change', updateMapMarkers);
}

// ==========================================
// Modal Events
// ==========================================

function setupModalEvents() {
    // Modal schließen bei Klick außerhalb
    document.getElementById('cityModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
}

// ==========================================
// FAQ Toggle
// ==========================================

function toggleFAQ(section) {
    const panel = document.getElementById(`faq-${section}`);
    const button = event.target;
    const allPanels = document.querySelectorAll('.faq-panel');
    const allButtons = document.querySelectorAll('.info-btn');
    
    allPanels.forEach(p => p.classList.remove('active'));
    allButtons.forEach(b => b.classList.remove('active'));
    
    if (panel && !panel.classList.contains('active')) {
        panel.classList.add('active');
        button.classList.add('active');
    }
}

// ==========================================
// Gewichtungen
// ==========================================

function updateWeightDisplay() {
    document.getElementById('weight-medien').addEventListener('input', function() {
        document.getElementById('weight-medien-value').textContent = this.value + '%';
    });
    document.getElementById('weight-zielgruppe').addEventListener('input', function() {
        document.getElementById('weight-zielgruppe-value').textContent = this.value + '%';
    });
    document.getElementById('weight-digital').addEventListener('input', function() {
        document.getElementById('weight-digital-value').textContent = this.value + '%';
    });
    document.getElementById('weight-wirtschaft').addEventListener('input', function() {
        document.getElementById('weight-wirtschaft-value').textContent = this.value + '%';
    });
    document.getElementById('weight-identitaet').addEventListener('input', function() {
        document.getElementById('weight-identitaet-value').textContent = this.value + '%';
    });
    document.getElementById('weight-praktikabilitaet').addEventListener('input', function() {
        document.getElementById('weight-praktikabilitaet-value').textContent = this.value + '%';
    });
}

function recalculateScores() {
    const newWeights = {
        medien: parseInt(document.getElementById('weight-medien').value) / 100,
        zielgruppe: parseInt(document.getElementById('weight-zielgruppe').value) / 100,
        digital: parseInt(document.getElementById('weight-digital').value) / 100,
        wirtschaft: parseInt(document.getElementById('weight-wirtschaft').value) / 100,
        identitaet: parseInt(document.getElementById('weight-identitaet').value) / 100,
        praktikabilitaet: parseInt(document.getElementById('weight-praktikabilitaet').value) / 100
    };
    
    // Prüfen ob Summe 100% ergibt
    const sum = Object.values(newWeights).reduce((a, b) => a + b, 0);
    if (Math.abs(sum - 1.0) > 0.01) {
        alert('Die Gewichtungen müssen zusammen 100% ergeben!');
        return;
    }
    
    // Scores neu berechnen
    cities.forEach(city => {
        let newScore = 0;
        newScore += city.scores.medien * newWeights.medien;
        newScore += city.scores.zielgruppe * newWeights.zielgruppe;
        newScore += city.scores.digital * newWeights.digital;
        newScore += city.scores.wirtschaft * newWeights.wirtschaft;
        newScore += city.scores.identitaet * newWeights.identitaet;
        newScore += city.scores.praktikabilitaet * newWeights.praktikabilitaet;
        city.score = Math.round(newScore * 4); // Skalierung auf 0-100
    });
    
    weights = newWeights;
    updateRankingTable();
    updateMapMarkers();
    updateSegmentAnalysis();
    updateAvgScore();
}

// ==========================================
// Karten-Funktionen
// ==========================================

function initializeMap() {
    map = L.map('map').setView([51.165, 10.451], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    updateMapMarkers();
}

function updateMapMarkers() {
    if (!map) return;
    
    // Alte Marker entfernen
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Filter-Werte holen
    const minScore = parseInt(document.getElementById('minScoreFilter').value);
    const minKaufkraft = parseInt(document.getElementById('minKaufkraft').value) || 0;
    const sizeFilter = document.getElementById('sizeFilter').value;
    const verlagFilter = document.getElementById('mapVerlagFilter').value;
    
    cities.forEach(city => {
        let show = true;
        
        // Score Filter
        if (city.score < minScore) show = false;
        
        // Kaufkraft Filter
        if (city.kaufkraft < minKaufkraft) show = false;
        
        // Größen-Filter
        if (sizeFilter !== 'all') {
            if (sizeFilter === 'klein' && (city.einwohner < 20000 || city.einwohner > 50000)) show = false;
            if (sizeFilter === 'mittel' && (city.einwohner < 50000 || city.einwohner > 100000)) show = false;
            if (sizeFilter === 'gross' && (city.einwohner < 100000 || city.einwohner > 500000)) show = false;
            if (sizeFilter === 'metro' && city.einwohner < 500000) show = false;
        }
        
        // Verlags-Filter
        if (verlagFilter === 'frei' && (city.funke || city.ippen || city.madsack)) show = false;
        if (verlagFilter === 'funke' && !city.funke) show = false;
        if (verlagFilter === 'ippen' && !city.ippen) show = false;
        if (verlagFilter === 'madsack' && !city.madsack) show = false;
        
        if (show) {
            const color = city.score >= 75 ? '#065f46' : city.score >= 60 ? '#84cc16' : '#fbbf24';
            const marker = L.circleMarker([city.lat, city.lon], {
                radius: Math.sqrt(city.einwohner / 1000) * 2,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
            
            let verlagInfo = [];
            if (city.funke) verlagInfo.push('Funke');
            if (city.ippen) verlagInfo.push('Ippen');
            if (city.madsack) verlagInfo.push('Madsack');
            
            marker.bindPopup(`
                <strong>${city.name}</strong><br>
                Score: ${city.score}<br>
                Einwohner: ${city.einwohner.toLocaleString()}<br>
                Kaufkraft: ${city.kaufkraft.toLocaleString()}€<br>
                ${verlagInfo.length > 0 ? 'Verlage: ' + verlagInfo.join(', ') : 'Keine Großverlage'}
            `);
            
            markers.push(marker);
        }
    });
}

// ==========================================
// Tabellen-Funktionen
// ==========================================

function sortTable(column) {
    if (currentSortColumn === column) {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = column;
        currentSortOrder = 'desc';
    }
    updateRankingTable();
}

function updateRankingTable() {
    const tbody = document.getElementById('rankingTableBody');
    const search = document.getElementById('searchFilter').value.toLowerCase();
    const bundesland = document.getElementById('bundeslandFilter').value;
    const verlagFilter = document.getElementById('verlagFilter').value;
    const sortBy = document.getElementById('sortBy').value;
    
    let filteredCities = cities.filter(city => {
        const matchesSearch = city.name.toLowerCase().includes(search);
        const matchesBundesland = bundesland === 'all' || city.bundesland === bundesland;
        
        let matchesVerlag = true;
        if (verlagFilter === 'frei') matchesVerlag = !city.funke && !city.ippen && !city.madsack;
        if (verlagFilter === 'funke') matchesVerlag = city.funke;
        if (verlagFilter === 'ippen') matchesVerlag = city.ippen;
        if (verlagFilter === 'madsack') matchesVerlag = city.madsack;
        
        return matchesSearch && matchesBundesland && matchesVerlag;
    });
    
    // Sortierung
    filteredCities.sort((a, b) => {
        switch(sortBy) {
            case 'score': return b.score - a.score;
            case 'einwohner': return b.einwohner - a.einwohner;
            case 'kaufkraft': return b.kaufkraft - a.kaufkraft;
            case 'name': return a.name.localeCompare(b.name);
            default: return 0;
        }
    });
    
    // Tabelle aufbauen
    tbody.innerHTML = '';
    filteredCities.forEach(city => {
        const scoreClass = city.score >= 75 ? 'score-high' : city.score >= 60 ? 'score-medium' : 'score-low';
        
        let verlagTags = '';
        if (city.funke) verlagTags += '<span class="publisher-tag publisher-funke">F</span>';
        if (city.ippen) verlagTags += '<span class="publisher-tag publisher-ippen">I</span>';
        if (city.madsack) verlagTags += '<span class="publisher-tag publisher-madsack">M</span>';
        if (!city.funke && !city.ippen && !city.madsack) verlagTags = '<span style="color: green;">✔</span>';
        
        const row = `
            <tr>
                <td><strong>${city.name}</strong></td>
                <td>${city.bundesland}</td>
                <td>${city.einwohner.toLocaleString()}</td>
                <td><span class="score-badge ${scoreClass}">${city.score}</span></td>
                <td>${verlagTags}</td>
                <td>${city.scores.medien}</td>
                <td>${city.scores.zielgruppe}</td>
                <td>${city.scores.digital}</td>
                <td>${city.scores.wirtschaft}</td>
                <td>${city.scores.identitaet}</td>
                <td>${city.scores.praktikabilitaet}</td>
                <td><button class="btn-details" onclick="showCityDetails('${city.name.replace(/'/g, "\\'")}')">Details</button></td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// ==========================================
// Segment-Analyse
// ==========================================

function updateSegmentAnalysis() {
    const segmentGrid = document.getElementById('segmentGrid');
    
    const segments = {
        'Top Testmärkte (Score 75+)': cities.filter(c => c.score >= 75).sort((a, b) => b.score - a.score).slice(0, 10),
        'Ohne Großverlage': cities.filter(c => !c.funke && !c.ippen && !c.madsack && c.score >= 65).sort((a, b) => b.score - a.score).slice(0, 10),
        'Universitätsstädte': cities.filter(c => c.typ.includes('Universitätsstadt')).sort((a, b) => b.score - a.score).slice(0, 10),
        'Speckgürtel': cities.filter(c => c.typ === 'Speckgürtel').sort((a, b) => b.score - a.score),
        'Ostdeutschland Top': cities.filter(c => ['Sachsen', 'Sachsen-Anhalt', 'Thüringen', 'Brandenburg', 'Mecklenburg-Vorpommern'].includes(c.bundesland)).sort((a, b) => b.score - a.score).slice(0, 10),
        'Mittelstädte (50-100k)': cities.filter(c => c.einwohner >= 50000 && c.einwohner <= 100000).sort((a, b) => b.score - a.score).slice(0, 10)
    };
    
    segmentGrid.innerHTML = '';
    for (const [title, segmentCities] of Object.entries(segments)) {
        if (segmentCities.length > 0) {
            const card = `
                <div class="segment-card">
                    <h3>${title}</h3>
                    <ul class="city-list">
                        ${segmentCities.slice(0, 8).map(c => {
                            const scoreClass = c.score >= 75 ? 'score-high' : c.score >= 60 ? 'score-medium' : 'score-low';
                            return `
                                <li>
                                    <span>${c.name}</span>
                                    <span class="score-badge ${scoreClass}">${c.score}</span>
                                </li>
                            `;
                        }).join('')}
                    </ul>
                </div>
            `;
            segmentGrid.innerHTML += card;
        }
    }
}

// ==========================================
// Vergleichs-Funktionen
// ==========================================

function setupComparisonSelects() {
    const city1Select = document.getElementById('city1Select');
    const city2Select = document.getElementById('city2Select');
    
    const sortedCities = [...cities].sort((a, b) => b.score - a.score);
    
    sortedCities.forEach(city => {
        city1Select.innerHTML += `<option value="${city.name}">${city.name} (Score: ${city.score})</option>`;
        city2Select.innerHTML += `<option value="${city.name}">${city.name} (Score: ${city.score})</option>`;
    });
    
    city1Select.addEventListener('change', updateComparison);
    city2Select.addEventListener('change', updateComparison);
}

function updateComparison() {
    const city1Name = document.getElementById('city1Select').value;
    const city2Name = document.getElementById('city2Select').value;
    
    if (!city1Name || !city2Name) return;
    
    const city1 = cities.find(c => c.name === city1Name);
    const city2 = cities.find(c => c.name === city2Name);
    
    // Details aktualisieren
    document.getElementById('city1Details').innerHTML = getCityDetailsHTML(city1);
    document.getElementById('city2Details').innerHTML = getCityDetailsHTML(city2);
    
    // Chart aktualisieren
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    comparisonChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Medien', 'Zielgruppe', 'Digital', 'Wirtschaft', 'Identität', 'Praktikabilität'],
            datasets: [
                {
                    label: city1.name,
                    data: Object.values(city1.scores),
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.2)'
                },
                {
                    label: city2.name,
                    data: Object.values(city2.scores),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)'
                }
            ]
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    max: 25
                }
            }
        }
    });
}

function getCityDetailsHTML(city) {
    let verlagInfo = [];
    if (city.funke) verlagInfo.push('Funke');
    if (city.ippen) verlagInfo.push('Ippen');
    if (city.madsack) verlagInfo.push('Madsack');
    
    return `
        <h4>${city.name}</h4>
        <p><strong>Bundesland:</strong> ${city.bundesland}</p>
        <p><strong>Einwohner:</strong> ${city.einwohner.toLocaleString()}</p>
        <p><strong>Kaufkraft:</strong> ${city.kaufkraft.toLocaleString()}€</p>
        <p><strong>Akademikerquote:</strong> ${city.akademikerquote}%</p>
        <p><strong>Verlage:</strong> ${verlagInfo.length > 0 ? verlagInfo.join(', ') : 'Keine Großverlage ✔'}</p>
        <p><strong>Gesamtscore:</strong> ${city.score}</p>
        <p><em>${city.description}</em></p>
    `;
}

// ==========================================
// Modal-Funktionen
// ==========================================

function showCityDetails(cityName) {
    const city = cities.find(c => c.name === cityName);
    const modal = document.getElementById('cityModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    let verlagInfo = [];
    if (city.funke) verlagInfo.push('Funke');
    if (city.ippen) verlagInfo.push('Ippen');
    if (city.madsack) verlagInfo.push('Madsack');
    
    modalTitle.textContent = city.name;
    modalBody.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
            <div>
                <h3>Basisdaten</h3>
                <p><strong>Bundesland:</strong> ${city.bundesland}</p>
                <p><strong>Einwohner:</strong> ${city.einwohner.toLocaleString()}</p>
                <p><strong>Kaufkraft:</strong> ${city.kaufkraft.toLocaleString()}€</p>
                <p><strong>Akademikerquote:</strong> ${city.akademikerquote}%</p>
                <p><strong>Stadttyp:</strong> ${city.typ}</p>
                <p><strong>Lokalzeitungen:</strong> ${city.lokalzeitungen}</p>
                <p><strong>Open Data:</strong> ${city.openData ? 'Ja' : 'Nein'}</p>
            </div>
            <div>
                <h3>Verlagslandschaft</h3>
                <p><strong>Funke:</strong> ${city.funke ? '✔ Präsent' : '✗ Nicht präsent'}</p>
                <p><strong>Ippen:</strong> ${city.ippen ? '✔ Präsent' : '✗ Nicht präsent'}</p>
                <p><strong>Madsack:</strong> ${city.madsack ? '✔ Präsent' : '✗ Nicht präsent'}</p>
                <p><strong>Status:</strong> ${verlagInfo.length > 0 ? '⚠️ Verlagskonkurrenz' : '✅ Freier Markt'}</p>
                <hr style="margin: 1rem 0;">
                <p><em>${city.description}</em></p>
            </div>
        </div>
        <canvas id="cityRadarChart" style="max-width: 400px; margin: 2rem auto;"></canvas>
    `;
    
    modal.classList.add('active');
    
    // Radar-Chart erstellen
    const ctx = document.getElementById('cityRadarChart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Medien', 'Zielgruppe', 'Digital', 'Wirtschaft', 'Identität', 'Praktikabilität'],
            datasets: [{
                label: city.name,
                data: Object.values(city.scores),
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.2)'
            }]
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    max: 25
                }
            }
        }
    });
}

function closeModal() {
    document.getElementById('cityModal').classList.remove('active');
}

// ==========================================
// Hilfsfunktionen
// ==========================================

function updateAvgScore() {
    const avg = Math.round(cities.reduce((sum, city) => sum + city.score, 0) / cities.length);
    document.getElementById('avgScore').textContent = avg;
}

// ==========================================
// Globale Funktionen für onclick-Handler
// ==========================================
window.toggleFAQ = toggleFAQ;
window.recalculateScores = recalculateScores;
window.showCityDetails = showCityDetails;
window.closeModal = closeModal;
window.sortTable = sortTable;
