function openComplaintDetails(
    complaintId,
    complainant,
    subject,
    description,
    category,
    priority,
    status,
    location,
    incidentDate
) {

    document.getElementById("drawerComplaintId").textContent =
        "#CP-2024-" + String(complaintId).padStart(3, "0");

    document.getElementById("drawerStatus").textContent =
        status || "Under Investigation";

    document.getElementById("drawerComplainant").textContent =
        complainant || "The complainant";

    document.getElementById("drawerDescription").textContent =
        description || "No incident description available.";

    document.getElementById("timelineComplainant").textContent =
        complainant || "the complainant";


    document.getElementById("complaintDrawer")
        .classList.add("active");

    document.getElementById("complaintOverlay")
        .classList.add("active");

    document.body.style.overflow = "hidden";
}


function closeComplaintDetails() {

    document.getElementById("complaintDrawer")
        .classList.remove("active");

    document.getElementById("complaintOverlay")
        .classList.remove("active");

    document.body.style.overflow = "";
}


/* Close using ESC */

document.addEventListener("keydown", function(event) {

    if (event.key === "Escape") {

        closeComplaintDetails();

    }

});