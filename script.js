// -----------------------------
// PASSWORD TOGGLE (safe version)
// -----------------------------
let password = document.getElementById("password");
let icon = document.getElementById("icon");

if (password && icon) {
    icon.onclick = function () {
        if (password.type === "password") {
            password.type = "text";
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
        } else {
            password.type = "password";
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
        }
    };
}



// -----------------------------
// HAMBURGER MENU FUNCTIONALITY
// -----------------------------

const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');
const overlay = document.getElementById('overlay');
const navbar = document.querySelector('.navbar');

hamburger.addEventListener('click', () => {
    const isOpen = hamburger.classList.contains('action');

    hamburger.classList.toggle('action');
    navMenu.classList.toggle('active');
    overlay.classList.toggle('action');
    navbar.classList.toggle('menu-open');

    document.body.style.overflow = isOpen ? 'auto' : 'hidden';
});

overlay.addEventListener('click', closeMenu);

document.querySelectorAll('.nev-butn').forEach(link => {
    link.addEventListener('click', closeMenu);
});

function closeMenu() {
    hamburger.classList.remove('action');
    navMenu.classList.remove('active');
    overlay.classList.remove('action');
    navbar.classList.remove('menu-open');
    document.body.style.overflow = 'auto';
}
