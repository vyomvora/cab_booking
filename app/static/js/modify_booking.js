/**
 * modify_booking.js - JavaScript for the modify booking page
 */

// Define initAutocomplete in global scope for Google Maps callback
function initAutocomplete() {
    // Listen for car type changes
    console.log("initAutocomplete function is running");
    const carTypeSelect = document.getElementById("car_type");
    if (carTypeSelect) {
        carTypeSelect.addEventListener("change", function() {
            calculateRoute(); // Recalculate when car changes
        });
    }

    // Initialize autocomplete for pickup location
    const pickupInput = document.getElementById("pickup");
    if (pickupInput) {
        const pickupAutocomplete = new google.maps.places.Autocomplete(pickupInput, {
            fields: ["formatted_address", "geometry", "name"],
            types: ["address"]
        });
        
        pickupAutocomplete.addListener("place_changed", () => {
            const place = pickupAutocomplete.getPlace();
            if (!place.geometry) {
                alert("Please select a location from the dropdown list");
                return;
            }
            
            // Store location data in hidden fields
            document.getElementById("pickup_lat").value = place.geometry.location.lat();
            document.getElementById("pickup_lng").value = place.geometry.location.lng();
            document.getElementById("pickup_address").value = place.formatted_address;
            
            // Use client-side calculation temporarily until form is submitted
            calculateRoute();
        });
    }
    
    // Initialize autocomplete for dropoff location
    const dropoffInput = document.getElementById("dropoff");
    if (dropoffInput) {
        const dropoffAutocomplete = new google.maps.places.Autocomplete(dropoffInput, {
            fields: ["formatted_address", "geometry", "name"],
            types: ["address"]
        });
        
        dropoffAutocomplete.addListener("place_changed", () => {
            const place = dropoffAutocomplete.getPlace();
            if (!place.geometry) {
                alert("Please select a location from the dropdown list");
                return;
            }
            
            // Store location data in hidden fields
            document.getElementById("dropoff_lat").value = place.geometry.location.lat();
            document.getElementById("dropoff_lng").value = place.geometry.location.lng();
            document.getElementById("dropoff_address").value = place.formatted_address;
            
            // Use client-side calculation temporarily until form is submitted
            calculateRoute();
        });
    }
    
    // Calculate initial route details on page load
    calculateRoute();
}

// Calculate route and update distance/duration/fare
function calculateRoute() {
    const pickupLat = document.getElementById("pickup_lat").value;
    const pickupLng = document.getElementById("pickup_lng").value;
    const dropoffLat = document.getElementById("dropoff_lat").value;
    const dropoffLng = document.getElementById("dropoff_lng").value;
    const carTypeSelect = document.getElementById("car_type");
    
    if (!pickupLat || !pickupLng || !dropoffLat || !dropoffLng) {
        return;
    }
    
    const pickupPos = new google.maps.LatLng(parseFloat(pickupLat), parseFloat(pickupLng));
    const dropoffPos = new google.maps.LatLng(parseFloat(dropoffLat), parseFloat(dropoffLng));
    
    // Use Google Maps Direction Service for more accurate routing
    const directionsService = new google.maps.DirectionsService();
    
    directionsService.route(
        {
            origin: pickupPos,
            destination: dropoffPos,
            travelMode: google.maps.TravelMode.DRIVING
        },
        (response, status) => {
            if (status === "OK") {
                const route = response.routes[0];
                const leg = route.legs[0];
                
                document.getElementById("distance").textContent = leg.distance.text;
                document.getElementById("duration").textContent = leg.duration.text;
                
                // Get selected car's rate_per_km from data attribute
                let ratePerKm = 2; // Default rate if none selected
                if (carTypeSelect.value) {
                    const selectedOption = carTypeSelect.options[carTypeSelect.selectedIndex];
                    ratePerKm = parseFloat(selectedOption.getAttribute("data-rate-per-km") || 2);
                }
                
                // Calculate fare based on distance and car rate
                const distanceKm = leg.distance.value / 1000;
                const fare = distanceKm * ratePerKm;
                document.getElementById("fare").textContent = "€" + fare.toFixed(2);
            } else {
                // If directions service fails, fall back to Distance Matrix
                fallbackDistanceCalculation(pickupPos, dropoffPos, carTypeSelect);
            }
        }
    );
}

// Fallback to Distance Matrix if Directions Service fails
function fallbackDistanceCalculation(pickupPos, dropoffPos, carTypeSelect) {
    const service = new google.maps.DistanceMatrixService();
    service.getDistanceMatrix(
        {
            origins: [pickupPos],
            destinations: [dropoffPos],
            travelMode: google.maps.TravelMode.DRIVING,
            unitSystem: google.maps.UnitSystem.METRIC
        },
        (response, status) => {
            if (status === "OK" && response.rows[0].elements[0].status === "OK") {
                const distance = response.rows[0].elements[0].distance;
                const duration = response.rows[0].elements[0].duration;
                
                document.getElementById("distance").textContent = distance.text;
                document.getElementById("duration").textContent = duration.text;
                
                // Get selected car's rate_per_km
                let ratePerKm = 2; // Default rate if none selected
                if (carTypeSelect.value) {
                    const selectedOption = carTypeSelect.options[carTypeSelect.selectedIndex];
                    ratePerKm = parseFloat(selectedOption.getAttribute("data-rate-per-km") || 2);
                }
                
                // Calculate fare using car-specific rate
                const distanceKm = distance.value / 1000;
                const fare = distanceKm * ratePerKm;
                document.getElementById("fare").textContent = "€" + fare.toFixed(2);
            } else {
                document.getElementById("distance").textContent = "Unable to calculate";
                document.getElementById("duration").textContent = "Unable to calculate";
                document.getElementById("fare").textContent = "Unable to calculate";
                console.error("Distance Matrix Error:", status);
            }
        }
    );
}

// Form validation before submission
document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.getElementById("booking-form");
    if (bookingForm) {
        bookingForm.addEventListener("submit", function(event) {
            const pickupLat = document.getElementById("pickup_lat").value;
            const dropoffLat = document.getElementById("dropoff_lat").value;
            const carType = document.getElementById("car_type").value;
            
            if (!pickupLat || !dropoffLat) {
                event.preventDefault();
                alert("Please select valid pickup and drop-off locations from the suggestions.");
                return false;
            }
            
            if (!carType) {
                event.preventDefault();
                alert("Please select a car type.");
                return false;
            }
            
            return true;
        });
    }
});