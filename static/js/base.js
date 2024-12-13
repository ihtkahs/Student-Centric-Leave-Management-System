// Toggle sidebar visibility
document.getElementById('sidebarToggle').addEventListener('click', () => {
    document.getElementById('wrapper').classList.toggle('sidebar-active');
});

document.addEventListener("DOMContentLoaded", function () {
    const leaveTypeDropdown = document.querySelector("#id_leave_type"); // Update with the correct ID for the dropdown
    const durationDropdown = document.querySelector("#id_duration");
    const dateField = document.querySelector("#dateField");
    const dateRangeField = document.querySelector("#dateRangeField");
    const proofField = document.querySelector("#proofField");

    // Handle Leave Type Dropdown
    leaveTypeDropdown.addEventListener("change", function () {
        const value = this.value;
        proofField.style.display = value === "medical" || value === "privilege" ? "block" : "none";
    });

    // Handle Duration Dropdown
    durationDropdown.addEventListener("change", function () {
        const value = this.value; // Get the selected duration
        dateField.style.display = value === "single" ? "block" : "none"; // Show single date input for single day
        dateRangeField.style.display = value === "multiple" ? "block" : "none"; // Show date range for multiple days
    });
});

  
