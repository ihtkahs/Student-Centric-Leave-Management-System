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
    const leaveForm = document.querySelector("#leaveForm");

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
    
    // Attach event listener to the form submit
    leaveForm.addEventListener("submit", function (event) {
        // Prevent the default form submission
        event.preventDefault();

        // Show SweetAlert confirmation dialog
        Swal.fire({
            title: "Are you sure?",
            text: "Do you want to submit this leave request?",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "Yes, submit it!",
            cancelButtonText: "Cancel",
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                // If confirmed, submit the form
                leaveForm.submit();
            }
        });
    });

    // Check if a success message exists and display it
    const successMessage = document.querySelector("#successMessage");
    if (successMessage) {
        Swal.fire({
            title: 'Success!',
            text: successMessage.innerText,
            icon: 'success',
            confirmButtonText: 'OK'
        }).then(() => {
            window.location.href = "/lms/apply/leave/";  // Redirect after closing the SweetAlert
        });
    }
});

function handleApproveAction(leaveId, action) {
    // Ask for comments when approving
    const userRole = "{{ user_role }}";
    Swal.fire({
        title: 'Add a Comment',
        input: 'textarea',
        inputPlaceholder: 'Enter your comment...',
        showCancelButton: true,
        confirmButtonText: 'Approve',
        cancelButtonText: 'Cancel',
        preConfirm: (comment) => {
            if (!comment) {
                Swal.showValidationMessage('Please add a comment');
                return false;
            }
            // Add comment and action to the form, then submit
            const form = document.getElementById('leave-form-' + leaveId);
            form.elements['comments'].value = comment;
            form.elements['action'].value = action;
            form.submit(); // Submit the form
        }
    }).then(() => {
        // Redirect based on role
        if (userRole === "counsellor") {
            window.location.href = "/lms/counsellor/approve/leave";
        } else if (userRole === "hod") {
            window.location.href = "/lms/hod/approve/leave";
        }
    });
}

function handleRejectAction(leaveId, action) {
    const userRole = "{{ user_role }}";
    // Ask for comments when approving
    Swal.fire({
        title: 'Add a Comment?',
        icon: 'warning',
        input: 'textarea',
        inputPlaceholder: 'Enter your comment...',
        showCancelButton: true,
        confirmButtonText: 'Yes, Reject',
        cancelButtonText: 'Cancel',
    }).then((result) => {
        if (result.isConfirmed) {
            // Add rejection action and submit
            const form = document.getElementById('leave-form-' + leaveId);
            form.elements['comments'].value = 'Rejected without specific comment';
            form.elements['action'].value = action;
            form.submit(); // Submit the form
        }
    }).then(() => {
        // Redirect based on role
        if (userRole === "counsellor") {
            window.location.href = "/lms/counsellor/approve/leave";
        } else if (userRole === "hod") {
            window.location.href = "/lms/hod/approve/leave";
        }
    });
}