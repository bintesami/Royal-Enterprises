// Crockery Wholesale Partnership Accounting System
// Phase 1 Frontend Initialization Script

document.addEventListener("DOMContentLoaded", function () {
    console.log("Crockery Accounting System initialized successfully.");

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll(".alert-dismissible, .alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            if (alert && alert.parentElement) {
                alert.style.transition = "opacity 0.4s ease";
                alert.style.opacity = "0";
                setTimeout(function () {
                    if (alert.parentElement) {
                        alert.remove();
                    }
                }, 400);
            }
        }, 5000);
    });

    // Formatting helper for currency values if needed
    window.formatPKR = function (amount) {
        return "PKR " + Number(amount).toLocaleString("en-PK", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    };
});
