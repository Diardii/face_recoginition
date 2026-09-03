console.log("Sidebar Loaded");

const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("overlay");
const toggleSidebar = document.getElementById("toggleSidebar");

if (toggleSidebar && sidebar && overlay) {

    toggleSidebar.addEventListener("click", () => {
        sidebar.classList.toggle("show");
        overlay.classList.toggle("show");
    });

    overlay.addEventListener("click", () => {
        sidebar.classList.remove("show");
        overlay.classList.remove("show");
    });

}