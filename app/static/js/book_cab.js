console.log("modify_booking.js loaded");
function initAutocomplete() {
    const carTypeSelect = document.getElementById("car_type");
    carTypeSelect.addEventListener("change", function() {
        previewRoute(); // Recalculate when car changes
    });
    // Initialize autocomplete for pickup location
    const pickupInput = document.getElementById("pickup");
    const pickupAutocomplete = new google.maps.places.Autocomplete(pickupInput, {
        fields: ["formatted_address", "geometry", "name"],
        types: ["address"]
    });
    console.log("Pickup input element:", pickupInput);
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
        document.getElementById("pickup-details").textContent = place.formatted_address;
        
        // Use client-side calculation temporarily until form is submitted
        previewRoute();
    });
    
    // Initialize autocomplete for dropoff location
    const dropoffInput = document.getElementById("dropoff");
    const dropoffAutocomplete = new google.maps.places.Autocomplete(dropoffInput, {
        fields: ["formatted_address", "geometry", "name"],
        types: ["address"]
    });
    console.log("Dropoff input element:", dropoffInput);
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
        document.getElementById("dropoff-details").textContent = place.formatted_address;
        
        // Use client-side calculation temporarily until form is submitted
        previewRoute();
    });
    
    // Set today's date as the default in the date field
    const dateInput = document.getElementById('date');
    const today = new Date();
    const formattedDate = today.toISOString().substr(0, 10);
    dateInput.value = formattedDate;
    dateInput.min = formattedDate; // Prevent selecting past dates
    
    // Set current time + 30 minutes as the default
    const timeInput = document.getElementById('time');
    today.setMinutes(today.getMinutes() + 30);
    const hours = today.getHours().toString().padStart(2, '0');
    const mins = today.getMinutes().toString().padStart(2, '0');
    timeInput.value = `${hours}:${mins}`;
}


// Temporarily calculate route preview using client-side Google Maps API
// This will be replaced by the server calculation when the form is submitted
function previewRoute() {
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
                
                // Get selected car's rate_per_km from data attribute
                let ratePerKm = 2;
                if (carTypeSelect.value) {
                    const selectedOption = carTypeSelect.options[carTypeSelect.selectedIndex];
                    ratePerKm = parseFloat(selectedOption.getAttribute("data-rate-per-km") || 2);
                }
                
                const baseFare = 5;
                const timeRate = 0.5; 
                
                const distanceKm = distance.value / 1000;
                const durationMin = duration.value / 60;
                
                const fare = baseFare + (distanceKm * ratePerKm) + (durationMin * timeRate);
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
document.getElementById("bookingForm").addEventListener("submit", function(event) {
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