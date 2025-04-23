document.addEventListener("DOMContentLoaded", function () {

// DOM element selection
  const tripTypeInputs = document.querySelectorAll('input[name="tripType"]');
  const returnDateInput = document.getElementById("returnDate");
  const originSelect = document.getElementById("origin");
  const destinationSelect = document.getElementById("destination");
  const searchButton = document.getElementById("searchFlights");
  const flightSelection = document.getElementById("flightSelection");
  const flightResultsTable = document.getElementById("flightResults");
  const passengerInfo = document.getElementById("passengerInfo");
  const contactInfo = document.getElementById("contactInfo");
  const bookingForm = document.getElementById("booking-form");
  const adultPassengers = document.getElementById("adultPassengers");
  const childPassengers = document.getElementById("childPassengers");
  const flightClassSelect = document.getElementById("flightClass");
  const passengerForms = document.getElementById("passengerForms");

  let selectedFlight = null;
  let selectedClass = null;

  tripTypeInputs.forEach((input) => {
    input.addEventListener("change", toggleReturnDate);
  });

  searchButton.addEventListener("click", searchFlights);

// Function definition
  function toggleReturnDate() {
    const isRoundTrip = document.getElementById("roundTrip").checked;
    returnDateInput.disabled = !isRoundTrip;
// Conditional logic
    if (isRoundTrip) {
      returnDateInput.setAttribute("required", "");
    } else {
      returnDateInput.removeAttribute("required");
    }
  }

// Function definition
  function searchFlights() {

    const origin = originSelect.value;
    const destination = destinationSelect.value;
    const departureDate = document.getElementById("departureDate").value;
    const travelClass = flightClassSelect.value;

// Conditional logic
    if (!origin || !destination || !departureDate || !travelClass) {
      alert("Please fill in all required fields.");
      return;
    }

// Conditional logic
    if (origin === destination) {
      alert("Origin and destination cannot be the same.");
      return;
    }

    searchButton.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i> Searching...';
    searchButton.disabled = true;

    const searchParams = new URLSearchParams({
      origin: origin,
      destination: destination,
      departure_date: departureDate,
      travel_class: travelClass,
    });

// API request to server
    fetch(`/bookings/api/search-flights/?${searchParams.toString()}`)
      .then((response) => {
// Conditional logic
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        displayFlights(data.flights, travelClass);
        searchButton.innerHTML =
          '<i class="fas fa-search me-2"></i> Search Flights';
        searchButton.disabled = false;
      })
      .catch((error) => {
        console.error("Error:", error);
        alert(
          "An error occurred while searching for flights. Please try again."
        );
        searchButton.innerHTML =
          '<i class="fas fa-search me-2"></i> Search Flights';
        searchButton.disabled = false;
      });
  }

// Function definition
  function displayFlights(flights, travelClass) {
    flightResultsTable.innerHTML = "";
    selectedClass = travelClass;

// Conditional logic
    if (flights.length === 0) {
      flightResultsTable.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-4">
                        <div class="alert alert-info mb-0">
                            <i class="fas fa-info-circle me-2"></i>
                            No flights found for the selected criteria. Please try different dates or airports.
                        </div>
                    </td>
                </tr>
            `;
    } else {
      flights.forEach((flight) => {
        const departureTime = new Date(flight.departure);
        const arrivalTime = new Date(flight.arrival);

        const row = document.createElement("tr");
        row.innerHTML = `
                    <td>
                        <strong>${flight.flight_number}</strong><br>
                        <small class="text-muted">${
                          flight.aircraft || "Aircraft TBA"
                        }</small>
                    </td>
                    <td>
                        <div><strong>${flight.origin.code}</strong> → <strong>${
          flight.destination.code
        }</strong></div>
                        <small class="text-muted">${flight.origin.city} to ${
          flight.destination.city
        }</small>
                    </td>
                    <td>
                        <div><strong>${formatTime(
                          departureTime
                        )}</strong> → <strong>${formatTime(
          arrivalTime
        )}</strong></div>
                        <small class="text-muted">${formatDate(
                          departureTime
                        )}</small>
                    </td>
                    <td>
                        <strong>${formatDuration(
                          flight.duration_minutes
                        )}</strong>
                    </td>
                    <td>
                        <strong>€${flight.price.toFixed(2)}</strong><br>
                        <small class="text-muted">${
                          flight.available_seats
                        } seats left</small>
                    </td>
                    <td>
                        <button type="button" class="btn btn-outline-primary select-flight" data-flight-id="${
                          flight.id
                        }">
                            Select
                        </button>
                    </td>
                `;

        flightResultsTable.appendChild(row);
      });

      document.querySelectorAll(".select-flight").forEach((button) => {
        button.addEventListener("click", function () {
          const flightId = this.getAttribute("data-flight-id");
          selectFlight(flightId, flights);
        });
      });
    }

    flightSelection.classList.remove("d-none");
    flightSelection.scrollIntoView({ behavior: "smooth" });
  }

// Function definition
  function selectFlight(flightId, flights) {

    selectedFlight = flights.find((flight) => flight.id == flightId);

// Conditional logic
    if (!selectedFlight) {
      console.error("Selected flight not found");
      return;
    }

    document.querySelectorAll("#flightResults tr").forEach((row) => {
      row.classList.remove("table-primary");
    });

    const selectedRow = document
      .querySelector(`button[data-flight-id="${flightId}"]`)
      .closest("tr");
    selectedRow.classList.add("table-primary");

    generatePassengerForms();
    passengerInfo.classList.remove("d-none");
    contactInfo.classList.remove("d-none");

    let selectedFlightInput = document.getElementById("selected_flight");
// Conditional logic
    if (!selectedFlightInput) {
      selectedFlightInput = document.createElement("input");
      selectedFlightInput.type = "hidden";
      selectedFlightInput.id = "selected_flight";
      selectedFlightInput.name = "selected_flight";
      bookingForm.appendChild(selectedFlightInput);
    }
    selectedFlightInput.value = flightId;

    let travelClassInput = document.getElementById("travel_class");
// Conditional logic
    if (!travelClassInput) {
      travelClassInput = document.createElement("input");
      travelClassInput.type = "hidden";
      travelClassInput.id = "travel_class";
      travelClassInput.name = "travel_class";
      bookingForm.appendChild(travelClassInput);
    }
    travelClassInput.value = selectedClass;

    passengerInfo.scrollIntoView({ behavior: "smooth" });
  }

// Function definition
  function generatePassengerForms() {
    const adultCount = parseInt(adultPassengers.value, 10);
    const childCount = parseInt(childPassengers.value, 10);
    const totalPassengers = adultCount + childCount;

    passengerForms.innerHTML = "";

    const adultCountInput = document.createElement("input");
    adultCountInput.type = "hidden";
    adultCountInput.name = "adult_count";
    adultCountInput.value = adultCount;
    passengerForms.appendChild(adultCountInput);

    const childCountInput = document.createElement("input");
    childCountInput.type = "hidden";
    childCountInput.name = "child_count";
    childCountInput.value = childCount;
    passengerForms.appendChild(childCountInput);

// Loop through items
    for (let i = 1; i <= totalPassengers; i++) {
      const isAdult = i <= adultCount;
      const passengerType = isAdult ? "Adult" : "Child";

      const passengerCard = document.createElement("div");
      passengerCard.className = "card mb-4";
      passengerCard.innerHTML = `
                <div class="card-header bg-light">
                    <h5 class="mb-0">Passenger ${i} (${passengerType})</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label for="passenger${i}_first_name" class="form-label">First Name</label>
                            <input type="text" class="form-control" id="passenger${i}_first_name" name="passenger${i}_first_name" required>
                        </div>
                        <div class="col-md-6">
                            <label for="passenger${i}_last_name" class="form-label">Last Name</label>
                            <input type="text" class="form-control" id="passenger${i}_last_name" name="passenger${i}_last_name" required>
                        </div>

                        <div class="col-md-6">
                            <label for="passenger${i}_dob" class="form-label">Date of Birth</label>
                            <input type="date" class="form-control" id="passenger${i}_dob" name="passenger${i}_dob" required>
                        </div>
                        <div class="col-md-6">
                            <label for="passenger${i}_gender" class="form-label">Gender</label>
                            <select class="form-select" id="passenger${i}_gender" name="passenger${i}_gender" required>
                                <option value="">Select Gender</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                                <option value="prefer_not_to_say">Prefer not to say</option>
                            </select>
                        </div>

                        <div class="col-md-6">
                            <label for="passenger${i}_nationality" class="form-label">Nationality</label>
                            <input type="text" class="form-control" id="passenger${i}_nationality" name="passenger${i}_nationality" required>
                        </div>

                        ${
                          isAdult
                            ? `
                        <div class="col-md-6">
                            <label for="passenger${i}_passport" class="form-label">Passport Number</label>
                            <input type="text" class="form-control" id="passenger${i}_passport" name="passenger${i}_passport" required>
                        </div>
                        <div class="col-md-6">
                            <label for="passenger${i}_passport_expiry" class="form-label">Passport Expiry Date</label>
                            <input type="date" class="form-control" id="passenger${i}_passport_expiry" name="passenger${i}_passport_expiry" required>
                        </div>
                        `
                            : ""
                        }

                        <div class="col-12">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="passenger${i}_special_assistance" name="passenger${i}_special_assistance">
                                <label class="form-check-label" for="passenger${i}_special_assistance">
                                    Requires special assistance
                                </label>
                            </div>
                        </div>

                        <div class="col-12 special-requirements d-none">
                            <label for="passenger${i}_special_requirements" class="form-label">Special Requirements</label>
                            <textarea class="form-control" id="passenger${i}_special_requirements" name="passenger${i}_special_requirements" rows="2"></textarea>
                        </div>

                        <div class="col-md-6">
                            <label for="passenger${i}_dietary" class="form-label">Dietary Requirements</label>
                            <select class="form-select" id="passenger${i}_dietary" name="passenger${i}_dietary">
                                <option value="">None</option>
                                <option value="vegetarian">Vegetarian</option>
                                <option value="vegan">Vegan</option>
                                <option value="gluten_free">Gluten Free</option>
                                <option value="dairy_free">Dairy Free</option>
                                <option value="nut_free">Nut Free</option>
                                <option value="other">Other (specify in special requirements)</option>
                            </select>
                        </div>
                    </div>
                </div>
            `;

      passengerForms.appendChild(passengerCard);
    }

    document
      .querySelectorAll('input[id^="passenger"][id$="_special_assistance"]')
      .forEach((checkbox) => {
        checkbox.addEventListener("change", function () {
          const specialReqDiv = this.closest(".row").querySelector(
            ".special-requirements"
          );
// Conditional logic
          if (this.checked) {
            specialReqDiv.classList.remove("d-none");
          } else {
            specialReqDiv.classList.add("d-none");
          }
        });
      });
  }

// Function definition
  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

// Function definition
  function formatDate(date) {
    return date.toLocaleDateString([], {
      weekday: "short",
      day: "numeric",
      month: "short",
    });
  }

// Function definition
  function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  }
});
