function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('.eye-icon');

    if (input.type === 'password') {
        input.type = 'text';
        icon.innerHTML = '<path d="M2 4.27L3.28 3L21 20.73L19.73 22L17.73 20H17.73C16.1 20.84 14.3 21.26 12.5 21.26C7.5 21.26 3.23 18.15 1.5 13.76C2.06 12.54 2.79 11.42 3.68 10.46L2 4.27M12.5 6.26C15.26 6.26 17.5 8.5 17.5 11.26C17.5 12.05 17.3 12.79 16.96 13.43L19.73 16.2C21.06 15.07 22.15 13.68 22.91 12.08C21.18 7.69 16.91 4.58 11.91 4.58C10.59 4.58 9.32 4.82 8.14 5.27L10.17 7.3C10.74 6.63 11.57 6.26 12.5 6.26M7.97 9.83C7.55 10.27 7.26 10.84 7.26 11.5C7.26 13.16 8.59 14.5 10.26 14.5C10.92 14.5 11.49 14.21 11.93 13.79L7.97 9.83Z"/>';
    } else {
        input.type = 'password';
        icon.innerHTML = '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5M12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5m0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3"/>';
    }
}

/**
 * Simple checkbox validation for Create Account button
 */

document.addEventListener('DOMContentLoaded', function() {
    const termsCheckbox = document.getElementById('termsAccepted');
    const createAccountBtn = document.querySelector('.create-account-btn');

    if (!termsCheckbox || !createAccountBtn) {
        return;
    }

    // Function to update button state
    function updateButtonState() {
        if (termsCheckbox.checked) {
            // Enable button
            createAccountBtn.disabled = false;
            createAccountBtn.classList.remove('disabled');
        } else {
            // Disable button
            createAccountBtn.disabled = true;
            createAccountBtn.classList.add('disabled');
        }
    }

    // Set initial state based on current checkbox state
    updateButtonState();

    // Listen for checkbox changes
    termsCheckbox.addEventListener('change', updateButtonState);
});