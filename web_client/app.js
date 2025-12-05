// Configuration de l'API Gateway
const GATEWAY_URL = 'http://localhost:8888';

// ===== PAGE LOADER =====
window.addEventListener('load', () => {
    setTimeout(() => {
        const loader = document.getElementById('page-loader');
        if (loader) {
            loader.classList.add('hidden');
        }
    }, 800);
});

// ===== HORLOGE EN TEMPS RÉEL =====
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// Mettre à jour l'horloge chaque seconde
setInterval(updateTime, 1000);
updateTime();

// ===== CARTE INTERACTIVE =====
// ===== AFFICHAGE DES DÉTAILS DE SERVICE =====
function showServiceDetails(serviceType) {
    // Basculer vers la section correspondante
    const btn = document.querySelector(`[data-service="${serviceType}"]`);
    if (btn) {
        btn.click();
    }
}

// ===== DASHBOARD VILLE =====
async function loadCityDashboard() {
    try {
        // Afficher un indicateur de chargement
        const dashTransportValue = document.getElementById('dash-transport-value');
        const dashAirValue = document.getElementById('dash-air-value');
        const dashTourismValue = document.getElementById('dash-tourism-value');
        const dashEmergencyValue = document.getElementById('dash-emergency-value');
        
        // Temporairement afficher "..."
        if (dashTransportValue) dashTransportValue.textContent = '...';
        if (dashAirValue) dashAirValue.textContent = '...';
        if (dashTourismValue) dashTourismValue.textContent = '...';
        if (dashEmergencyValue) dashEmergencyValue.textContent = '...';
        
        const response = await fetch(`${GATEWAY_URL}/api/orchestration/city-dashboard`);
        const data = await response.json();
        
        console.log('Dashboard data:', data); // Pour debug
        
        // Mise à jour des statistiques de transport
        if (dashTransportValue && data.transport) {
            const operationalLines = data.transport.operational || 0;
            const totalLines = data.transport.total_lines || 0;
            dashTransportValue.textContent = `${operationalLines}/${totalLines}`;
            console.log('Transport:', `${operationalLines}/${totalLines}`);
        }
        
        // Mise à jour de la qualité de l'air
        if (dashAirValue && data.air_quality) {
            const aqi = data.air_quality.average_aqi || 0;
            dashAirValue.textContent = aqi;
            console.log('Air Quality AQI:', aqi);
        }
        
        // Mise à jour du tourisme
        if (dashTourismValue && data.tourism) {
            const openAttractions = data.tourism.currently_open || 0;
            const totalAttractions = data.tourism.total_attractions || 0;
            dashTourismValue.textContent = `${openAttractions}/${totalAttractions}`;
            console.log('Tourism:', `${openAttractions}/${totalAttractions}`);
        }
        
        // Mise à jour des urgences
        if (dashEmergencyValue && data.emergency) {
            const availableVehicles = data.emergency.available_vehicles || 0;
            const totalVehicles = data.emergency.total_vehicles || 0;
            dashEmergencyValue.textContent = `${availableVehicles}/${totalVehicles}`;
            console.log('Emergency:', `${availableVehicles}/${totalVehicles}`);
        }
        
        // Mise à jour du statut général de la ville
        const cityStatusText = document.getElementById('city-status-text');
        if (cityStatusText) {
            const status = data.city_status || 'Normal';
            const timestamp = new Date().toLocaleTimeString('fr-FR');
            cityStatusText.textContent = `État général : ${status} (mis à jour à ${timestamp})`;
        }
        
        // Mise à jour des alertes
        const alertsList = document.getElementById('alerts-list');
        const alertsSection = document.getElementById('alerts-section');
        if (alertsList && data.alerts && data.alerts.length > 0) {
            alertsList.innerHTML = data.alerts.map(alert => 
                `<div class="alert-item">${alert}</div>`
            ).join('');
            if (alertsSection) {
                alertsSection.style.display = 'block';
            }
        } else {
            if (alertsSection) {
                alertsSection.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Erreur lors du chargement du dashboard ville:', error);
        // Réafficher "-" en cas d'erreur
        const dashTransportValue = document.getElementById('dash-transport-value');
        const dashAirValue = document.getElementById('dash-air-value');
        const dashTourismValue = document.getElementById('dash-tourism-value');
        const dashEmergencyValue = document.getElementById('dash-emergency-value');
        
        if (dashTransportValue) dashTransportValue.textContent = 'Erreur';
        if (dashAirValue) dashAirValue.textContent = 'Erreur';
        if (dashTourismValue) dashTourismValue.textContent = 'Erreur';
        if (dashEmergencyValue) dashEmergencyValue.textContent = 'Erreur';
    }
}

// Navigation entre les sections
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const service = btn.dataset.service;
        
        // Mettre à jour les boutons actifs
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Mettre à jour les sections actives
        document.querySelectorAll('.service-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(service).classList.add('active');
        
        // Charger le dashboard ville si c'est la section sélectionnée
        if (service === 'dashboard') {
            loadCityDashboard();
        }
    });
});

// Vérifier le statut de santé au chargement
// ============================================
// SERVICE TRANSPORT (REST)
// ============================================

async function loadTransports() {
    const contentArea = document.getElementById('transport-content');
    contentArea.innerHTML = '<p>Chargement...</p>';
    
    try {
        const response = await fetch(`${GATEWAY_URL}/api/transport/transports`);
        const transports = await response.json();
        
        if (transports.length === 0) {
            contentArea.innerHTML = '<p>Aucun transport disponible</p>';
            return;
        }
        
        let html = '<table class="data-table"><thead><tr>';
        html += '<th>ID</th><th>Mode</th><th>Route</th><th>Statut</th><th>Date</th><th>Actions</th>';
        html += '</tr></thead><tbody>';
        
        transports.forEach(t => {
            const statusClass = t.status === 'operationnel' ? 'status-ok' : 'status-warning';
            const adminButtons = isAdmin() ? `
                <button onclick="showEditTransportForm(${t.id}, '${t.mode}', '${t.route}', '${t.status}')" class="btn-edit">Modifier</button>
                <button onclick="deleteTransport(${t.id})" class="btn-delete">Supprimer</button>
            ` : '<span class="text-muted">Actions réservées aux admins</span>';
            
            html += `<tr>
                <td>${t.id}</td>
                <td>${t.mode}</td>
                <td>${t.route}</td>
                <td><span class="${statusClass}">${t.status}</span></td>
                <td>${new Date(t.created_at).toLocaleDateString('fr-FR')}</td>
                <td>${adminButtons}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        contentArea.innerHTML = html;
    } catch (error) {
        contentArea.innerHTML = `<p class="error">❌ Erreur: ${error.message}</p>`;
    }
}

function showAddTransportForm() {
    if (!isAdmin()) {
        alert('❌ Fonctionnalité réservée aux administrateurs. Connectez-vous avec un compte admin.');
        showLoginModal();
        return;
    }
    document.getElementById('add-transport-form').style.display = 'block';
}

function hideAddTransportForm() {
    document.getElementById('add-transport-form').style.display = 'none';
}

async function createTransport() {
    const mode = document.getElementById('transport-mode').value;
    const route = document.getElementById('transport-route').value;
    const status = document.getElementById('transport-status').value;
    
    if (!mode || !route) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${GATEWAY_URL}/api/transport/transports`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode, route, status })
        });
        
        if (response.ok) {
            alert('✅ Transport créé avec succès');
            hideAddTransportForm();
            loadTransports();
            // Reset form
            document.getElementById('transport-mode').value = '';
            document.getElementById('transport-route').value = '';
        } else {
            alert('❌ Erreur lors de la création');
        }
    } catch (error) {
        alert(`❌ Erreur: ${error.message}`);
    }
}

async function deleteTransport(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce transport ?')) return;
    
    try {
        const response = await authenticatedFetch(`${GATEWAY_URL}/api/transport/transports/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('✅ Transport supprimé');
            loadTransports();
        } else {
            alert('❌ Erreur lors de la suppression');
        }
    } catch (error) {
        alert(`❌ Erreur: ${error.message}`);
    }
}

function showEditTransportForm(id, mode, route, status) {
    const form = document.getElementById('edit-transport-form');
    document.getElementById('edit-transport-id').value = id;
    document.getElementById('edit-transport-mode').value = mode;
    document.getElementById('edit-transport-route').value = route;
    document.getElementById('edit-transport-status').value = status;
    form.style.display = 'block';
}

function hideEditTransportForm() {
    document.getElementById('edit-transport-form').style.display = 'none';
}

async function updateTransport() {
    const id = document.getElementById('edit-transport-id').value;
    const mode = document.getElementById('edit-transport-mode').value;
    const route = document.getElementById('edit-transport-route').value;
    const status = document.getElementById('edit-transport-status').value;
    
    if (!mode || !route) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${GATEWAY_URL}/api/transport/transports/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode, route, status })
        });
        
        if (response.ok) {
            alert('✅ Transport modifié avec succès');
            hideEditTransportForm();
            loadTransports();
        } else {
            alert('❌ Erreur lors de la modification');
        }
    } catch (error) {
        alert(`❌ Erreur: ${error.message}`);
    }
}

// ============================================
// SERVICE TOURISME (GraphQL)
// ============================================

async function loadAttractions() {
    const contentArea = document.getElementById('tourism-content');
    contentArea.innerHTML = '<p>Chargement...</p>';
    
    try {
        const response = await fetch(`${GATEWAY_URL}/api/tourism/attractions`);
        const attractions = await response.json();
        
        if (attractions.length === 0) {
            contentArea.innerHTML = '<p>Aucune attraction disponible</p>';
            return;
        }
        
        let html = '<div class="attractions-grid">';
        
        attractions.forEach(a => {
            const stars = '⭐'.repeat(Math.floor(a.rating || 0));
            const price = '€'.repeat(a.priceLevel || 1);
            html += `
                <div class="attraction-card">
                    <h3>${a.name}</h3>
                    <p class="category">${a.category}</p>
                    <p class="description">${a.description || 'Pas de description'}</p>
                    <p class="location">📍 ${a.address}, ${a.city}</p>
                    <p class="rating">${stars} (${a.rating || 'N/A'})</p>
                    <p class="price">${price}</p>
                    <p class="hours">🕐 ${a.openingHours || 'Horaires non disponibles'}</p>
                    <p class="status ${a.isOpen === 'open' ? 'status-ok' : 'status-warning'}">
                        ${a.isOpen === 'open' ? '✅ Ouvert' : '❌ Fermé'}
                    </p>
                </div>
            `;
        });
        
        html += '</div>';
        contentArea.innerHTML = html;
    } catch (error) {
        contentArea.innerHTML = `<p class="error">❌ Erreur: ${error.message}</p>`;
    }
}

// ============================================
// SERVICE QUALITÉ DE L'AIR (SOAP)
// ============================================

async function loadAirQuality() {
    const contentArea = document.getElementById('air-quality-content');
    contentArea.innerHTML = '<p class="loading">⏳ Chargement des mesures...</p>';
    
    try {
        const response = await fetch(`${GATEWAY_URL}/api/air-quality/measures`);
        const data = await response.json();
        
        // Le Gateway retourne juste les infos SOAP, pas les vraies données
        if (data.message && data.wsdl) {
            contentArea.innerHTML = `
                <div class="info-box">
                    <h4>📡 Service SOAP Qualité de l'Air</h4>
                    <p><strong>Status:</strong> Opérationnel</p>
                    <p><strong>WSDL:</strong> <code>${data.wsdl}</code></p>
                    <p><strong>Opérations disponibles:</strong></p>
                    <ul>
                        ${data.operations.map(op => `<li>${op}</li>`).join('')}
                    </ul>
                    <p class="note">💡 Utilisez le Dashboard Ville pour voir les statistiques agrégées de qualité d'air.</p>
                </div>
            `;
            return;
        }
        
        const measures = data.measures || data;
        
        if (!measures || measures.length === 0) {
            contentArea.innerHTML = '<p>Aucune mesure disponible</p>';
            return;
        }
        
        let html = '<div class="air-measures-grid">';
        
        measures.forEach(m => {
            const aqi = m.aqi || 0;
            let aqiClass = 'aqi-good';
            let aqiLabel = 'Bon';
            
            if (aqi > 150) {
                aqiClass = 'aqi-verybad';
                aqiLabel = 'Très mauvais';
            } else if (aqi > 100) {
                aqiClass = 'aqi-bad';
                aqiLabel = 'Mauvais';
            } else if (aqi > 50) {
                aqiClass = 'aqi-moderate';
                aqiLabel = 'Modéré';
            }
            
            html += `
                <div class="measure-card">
                    <div class="measure-header">
                        <span class="station-name">📍 ${m.station || m.zone}</span>
                        <span class="aqi-badge-small ${aqiClass}">${aqi}</span>
                    </div>
                    <p style="color: var(--text-secondary); margin-bottom: 1rem;">${aqiLabel}</p>
                    <div class="measure-details">
                        <div class="measure-detail">
                            <span class="measure-label">PM2.5</span>
                            <span class="measure-value">${m.pm25 || 'N/A'} µg/m³</span>
                        </div>
                        <div class="measure-detail">
                            <span class="measure-label">PM10</span>
                            <span class="measure-value">${m.pm10 || 'N/A'} µg/m³</span>
                        </div>
                        <div class="measure-detail">
                            <span class="measure-label">NO2</span>
                            <span class="measure-value">${m.no2 || 'N/A'} µg/m³</span>
                        </div>
                        <div class="measure-detail">
                            <span class="measure-label">O3</span>
                            <span class="measure-value">${m.o3 || 'N/A'} µg/m³</span>
                        </div>
                    </div>
                    <p style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-secondary);">
                        📅 ${new Date(m.timestamp || m.date).toLocaleString('fr-FR')}
                    </p>
                </div>
            `;
        });
        
        html += '</div>';
        contentArea.innerHTML = html;
    } catch (error) {
        contentArea.innerHTML = `<p class="error">❌ Erreur: ${error.message}</p>`;
    }
}

// ============================================
// SERVICE URGENCES (gRPC)
// ============================================

async function loadEmergencyData() {
    const vehiclesDiv = document.getElementById('emergency-vehicles');
    const interventionsDiv = document.getElementById('emergency-interventions');
    
    vehiclesDiv.innerHTML = '<p class="loading">⏳ Chargement...</p>';
    interventionsDiv.innerHTML = '<p class="loading">⏳ Chargement...</p>';
    
    try {
        // Charger les véhicules
        const vehiclesResponse = await fetch(`${GATEWAY_URL}/api/emergency/vehicles`);
        const vehiclesData = await vehiclesResponse.json();
        const vehicles = vehiclesData.vehicles || [];
        
        console.log('Véhicules reçus:', vehicles);
        
        if (vehicles.length === 0) {
            vehiclesDiv.innerHTML = '<p>Aucun véhicule</p>';
        } else {
            let vehiclesHtml = '';
            vehicles.forEach(v => {
                const statusClass = v.status === 'available' ? 'status-available' : 
                                  v.status === 'on_mission' ? 'status-busy' : 'status-maintenance';
                const statusText = v.status === 'available' ? '✅ Disponible' : 
                                 v.status === 'on_mission' ? '🚨 En intervention' : '🔧 Maintenance';
                const typeIcon = v.vehicle_type === 'ambulance' ? '🚑' : 
                               v.vehicle_type === 'fire_truck' ? '🚒' : '🚓';
                
                const vehicleName = v.identifier || `Véhicule ${v.id}`;
                const vehicleType = v.vehicle_type === 'ambulance' ? 'Ambulance' : 
                                   v.vehicle_type === 'fire_truck' ? 'Camion de pompiers' : 'Voiture de police';
                
                vehiclesHtml += `
                    <div class="vehicle-card">
                        <div class="vehicle-header">
                            <span class="vehicle-name">${typeIcon} ${vehicleName}</span>
                            <span class="vehicle-status ${statusClass}">${statusText}</span>
                        </div>
                        <div class="vehicle-details">
                            <div class="detail-row">
                                <span class="detail-label">Type:</span>
                                <span>${vehicleType}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Station:</span>
                                <span>📍 ${v.station || 'Non assigné'}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Équipage:</span>
                                <span>👥 ${v.crew_size} personnes</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            vehiclesDiv.innerHTML = vehiclesHtml;
        }
        
        // Charger les interventions
        const interventionsResponse = await fetch(`${GATEWAY_URL}/api/emergency/interventions`);
        const interventionsData = await interventionsResponse.json();
        const interventions = interventionsData.interventions || [];
        
        console.log('Interventions reçues:', interventions);
        
        if (interventions.length === 0) {
            interventionsDiv.innerHTML = '<p>Aucune intervention active</p>';
        } else {
            let interventionsHtml = '';
            interventions.forEach(i => {
                const priorityClass = i.priority === 'critical' ? 'priority-critical' : 
                                     i.priority === 'high' ? 'priority-high' : 'priority-medium';
                const priorityText = i.priority === 'critical' ? '🔴 Critique' : 
                                    i.priority === 'high' ? '🟠 Haute' : '🟡 Moyenne';
                const statusClass = i.status === 'in_progress' ? 'status-active' : 
                                   i.status === 'pending' ? 'status-pending' : 'status-available';
                const statusText = i.status === 'in_progress' ? '🚨 En cours' : 
                                  i.status === 'pending' ? '⏳ En attente' : '✅ Terminée';
                
                const typeText = i.intervention_type === 'medical' ? '🏥 Médical' :
                                i.intervention_type === 'fire' ? '🔥 Incendie' :
                                i.intervention_type === 'accident' ? '🚗 Accident' : '🚔 Crime';
                
                interventionsHtml += `
                    <div class="intervention-card">
                        <div class="intervention-header">
                            <span class="intervention-title">${typeText}</span>
                            <span class="intervention-priority ${priorityClass}">${priorityText}</span>
                        </div>
                        <div class="intervention-status-row">
                            <span class="${statusClass}">${statusText}</span>
                        </div>
                        <div class="intervention-details">
                            <div class="detail-row">
                                <span class="detail-label">📍 Adresse:</span>
                                <span>${i.address || 'Non spécifiée'}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">📝 Description:</span>
                                <span>${i.description || 'Aucune description'}</span>
                            </div>
                            ${i.assigned_vehicle_id ? `
                            <div class="detail-row">
                                <span class="detail-label">🚗 Véhicule:</span>
                                <span>ID ${i.assigned_vehicle_id}</span>
                            </div>
                            ` : '<div class="detail-row"><span class="detail-label">🚗 Véhicule:</span><span>⚠️ Non assigné</span></div>'}
                        </div>
                    </div>
                `;
            });
            interventionsDiv.innerHTML = interventionsHtml;
        }
        
    } catch (error) {
        vehiclesDiv.innerHTML = `<p class="error">❌ Erreur: ${error.message}</p>`;
        interventionsDiv.innerHTML = `<p class="error">❌ Erreur: ${error.message}</p>`;
    }
}

// ============================================
// ORCHESTRATION - PLANIFICATEUR DE TRAJET
// ============================================

async function planTrip() {
    const zone = document.getElementById('zone-select').value;
    const loadingEl = document.getElementById('trip-loading');
    const resultEl = document.getElementById('trip-result');
    
    // Afficher le loading
    loadingEl.style.display = 'block';
    resultEl.style.display = 'none';
    
    try {
        const response = await fetch(`${GATEWAY_URL}/api/orchestration/plan-trip?zone=${encodeURIComponent(zone)}`);
        const data = await response.json();
        
        // Masquer le loading
        loadingEl.style.display = 'none';
        resultEl.style.display = 'grid';
        
        // Mettre à jour la qualité de l'air
        const aqiBadge = document.getElementById('aqi-badge');
        const aqiValue = document.getElementById('aqi-value');
        const airStatus = document.getElementById('air-status');
        
        aqiValue.textContent = data.air_quality.aqi;
        airStatus.textContent = data.air_quality.status;
        
        // Couleur du badge selon l'AQI
        aqiBadge.className = 'aqi-badge ' + data.air_quality.color;
        
        // Mettre à jour la recommandation
        document.getElementById('recommendation-text').textContent = data.recommendation;
        
        // Mettre à jour les transports recommandés
        const transportsContainer = document.getElementById('recommended-transports');
        
        if (data.transports && data.transports.length > 0) {
            let html = '';
            data.transports.forEach(t => {
                const icon = getTransportIcon(t.mode);
                html += `
                    <div class="transport-item">
                        <div class="transport-info">
                            <span class="transport-mode">${icon}</span>
                            <div>
                                <div class="transport-route"><strong>${t.mode}</strong> - ${t.route}</div>
                            </div>
                        </div>
                        <span class="status-ok">✅ Disponible</span>
                    </div>
                `;
            });
            transportsContainer.innerHTML = html;
        } else {
            transportsContainer.innerHTML = '<p>Aucun transport disponible pour cette zone</p>';
        }
        
    } catch (error) {
        loadingEl.style.display = 'none';
        resultEl.style.display = 'block';
        document.getElementById('recommendation-text').innerHTML = 
            `<span class="error">❌ Erreur lors de la planification: ${error.message}</span>`;
    }
}

function getTransportIcon(mode) {
    const icons = {
        'Bus': '🚌',
        'Métro': '🚇',
        'Tramway': '🚊',
        'Train': '🚂',
        'Vélo': '🚴',
        'Taxi': '🚕'
    };
    return icons[mode] || '🚗';
}

// ===== INITIALISATION AU CHARGEMENT =====
document.addEventListener('DOMContentLoaded', () => {
    // Charger le Dashboard Ville par défaut
    loadCityDashboard();
    
    // Mettre à jour le statut de connexion
    const connectionStatus = document.getElementById('connection-status');
    if (connectionStatus) {
        const statusText = connectionStatus.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = 'Connecté';
        }
    }
});

// Recharger le dashboard toutes les 30 secondes
setInterval(() => {
    // Recharger seulement si on est sur le dashboard
    const dashboardSection = document.getElementById('dashboard');
    if (dashboardSection && dashboardSection.classList.contains('active')) {
        loadCityDashboard();
    }
}, 30000);
