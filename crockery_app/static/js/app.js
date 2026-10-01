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

    // Mobile Sidebar Drawer Toggle
    window.toggleSidebar = function () {
        const sb = document.getElementById("sidebar");
        const bd = document.getElementById("sidebarBackdrop");
        if (sb) sb.classList.toggle("show");
        if (bd) bd.classList.toggle("show");
    };

    window.closeSidebar = function () {
        const sb = document.getElementById("sidebar");
        const bd = document.getElementById("sidebarBackdrop");
        if (sb) sb.classList.remove("show");
        if (bd) bd.classList.remove("show");
    };
});

