// Live Delivery Tracking System

let map;
let deliveryMarker;
let routePolyline;
let etaInterval;
let locationInterval;
const ORDER_ID = window.location.pathname.split('/').pop();

// Initialize map and start tracking
function initTracking() {
    const pickup = { lat: parseFloat(document.getElementById('pickup-lat').value), lng: parseFloat(document.getElementById('pickup-lng').value) };
    const delivery = { lat: parseFloat(document.getElementById('delivery-lat').value), lng: parseFloat(document.getElementById('delivery-lng').value) };

    map = new google.maps.Map(document.getElementById('tracking-map'), {
        center: pickup,
        zoom: 12,
        mapTypeControl: false,
        streetViewControl: false
    });

    // Add pickup marker
    new google.maps.Marker({
        position: pickup,
        map: map,
        title: 'Pickup Location',
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="20" cy="20" r="18" fill="#28a745" stroke="white" stroke-width="3"/>
                    <text x="20" y="25" text-anchor="middle" fill="white" font-size="12" font-weight="bold">P</text>
                </svg>
            `),
            scaledSize: new google.maps.Size(40, 40)
        }
    });

    // Add delivery marker
    new google.maps.Marker({
        position: delivery,
        map: map,
        title: 'Delivery Location',
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="20" cy="20" r="18" fill="#dc3545" stroke="white" stroke-width="3"/>
                    <text x="20" y="25" text-anchor="middle" fill="white" font-size="12" font-weight="bold">D</text>
                </svg>
            `),
            scaledSize: new google.maps.Size(40, 40)
        }
    });

    // Initialize delivery person marker
    deliveryMarker = new google.maps.Marker({
        map: map,
        title: 'Delivery Person',
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="15" cy="15" r="13" fill="#007bff" stroke="white" stroke-width="2"/>
                    <path d="M8 12 L15 6 L22 12 L15 18 Z" fill="white"/>
                </svg>
            `),
            scaledSize: new google.maps.Size(30, 30)
        }
    });

    // Start live tracking
    startLiveTracking();
    startEtaUpdates();
}

// Start live location tracking
function startLiveTracking() {
    updateDeliveryLocation();

    // Update location every 30 seconds
    locationInterval = setInterval(updateDeliveryLocation, 30000);
}

// Update delivery person's location
async function updateDeliveryLocation() {
    try {
        const response = await fetch(`/api/get-delivery-location/${ORDER_ID}`);
        const data = await response.json();

        if (data.success && data.location) {
            const position = {
                lat: data.location.lat,
                lng: data.location.lng
            };

            deliveryMarker.setPosition(position);
            deliveryMarker.setTitle(`Delivery Person: ${data.location.delivery_person}`);

            // Update route if we have both pickup and current location
            updateRoute(position);

            // Show last updated time
            updateLastUpdated(data.location.updated_at);

            // Hide "waiting for location" message
            document.getElementById('location-waiting').style.display = 'none';
            document.getElementById('live-tracking-info').style.display = 'block';
        } else {
            // Show waiting message
            document.getElementById('location-waiting').style.display = 'block';
            document.getElementById('live-tracking-info').style.display = 'none';
        }
    } catch (error) {
        console.error('Error updating delivery location:', error);
    }
}

// Update route from delivery person to destination
function updateRoute(deliveryPosition) {
    const deliveryLat = parseFloat(document.getElementById('delivery-lat').value);
    const deliveryLng = parseFloat(document.getElementById('delivery-lng').value);
    const destination = { lat: deliveryLat, lng: deliveryLng };

    // Remove existing route
    if (routePolyline) {
        routePolyline.setMap(null);
    }

    // Create new route
    routePolyline = new google.maps.Polyline({
        path: [deliveryPosition, destination],
        geodesic: true,
        strokeColor: '#007bff',
        strokeOpacity: 0.8,
        strokeWeight: 3,
        icons: [{
            icon: {
                path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                scale: 3,
                strokeColor: '#007bff'
            },
            offset: '100%'
        }]
    });

    routePolyline.setMap(map);

    // Fit map to show both markers and route
    const bounds = new google.maps.LatLngBounds();
    bounds.extend(deliveryPosition);
    bounds.extend(destination);
    map.fitBounds(bounds);
}

// Start ETA updates
function startEtaUpdates() {
    updateETA();

    // Update ETA every 60 seconds
    etaInterval = setInterval(updateETA, 60000);
}

// Update estimated time of arrival
async function updateETA() {
    try {
        const response = await fetch(`/api/calculate-eta/${ORDER_ID}`);
        const data = await response.json();

        if (data.success) {
            const etaElement = document.getElementById('eta-display');
            const distanceElement = document.getElementById('distance-display');

            etaElement.textContent = `${data.eta_minutes} minutes`;
            distanceElement.textContent = `${data.distance_km} km`;

            // Update status based on ETA
            if (data.eta_minutes <= 5) {
                etaElement.style.color = '#28a745'; // Green
                etaElement.textContent = 'Arriving soon!';
            } else if (data.eta_minutes <= 15) {
                etaElement.style.color = '#ffc107'; // Yellow
            } else {
                etaElement.style.color = '#dc3545'; // Red
            }
        }
    } catch (error) {
        console.error('Error updating ETA:', error);
    }
}

// Update last location update time
function updateLastUpdated(timestamp) {
    const lastUpdatedElement = document.getElementById('last-updated');
    const updatedTime = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now - updatedTime) / 60000);

    if (diffMinutes < 1) {
        lastUpdatedElement.textContent = 'Just now';
    } else if (diffMinutes === 1) {
        lastUpdatedElement.textContent = '1 minute ago';
    } else {
        lastUpdatedElement.textContent = `${diffMinutes} minutes ago`;
    }
}

// Stop tracking when page unloads
window.addEventListener('beforeunload', function() {
    if (locationInterval) clearInterval(locationInterval);
    if (etaInterval) clearInterval(etaInterval);
});

// Legacy function for backward compatibility
function updateDeliveryEta(orderId) {
    // This function is kept for backward compatibility
    // The new system uses real-time updates instead
}
