function toggleDropdown() {
    const dropdown = document.getElementById('profileDropdown');
    dropdown.classList.toggle('active');
}

function toggleMobileMenu() {
    const mobileNav = document.getElementById('mobileNav');
    const mobileNavOverlay = document.getElementById('mobileNavOverlay');
    const body = document.body;

    mobileNav.classList.toggle('active');
    mobileNavOverlay.classList.toggle('active');
    body.classList.toggle('mobile-menu-open');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('profileDropdown');
    const profileIcon = document.querySelector('.profile-icon');

    if (profileIcon && !profileIcon.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});

// Close mobile menu on window resize
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        const mobileNav = document.getElementById('mobileNav');
        const mobileNavOverlay = document.getElementById('mobileNavOverlay');
        const body = document.body;

        mobileNav.classList.remove('active');
        mobileNavOverlay.classList.remove('active');
        body.classList.remove('mobile-menu-open');
    }
});