function closeFlashMessage(button) {
    const message = button.parentElement;
    message.style.animation = 'slideOut 0.3s ease-out forwards';
    setTimeout(() => {
        message.remove();
    }, 300);
}

document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((message, index) => {
        setTimeout(() => {
            if (message.parentElement) {
                message.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => {
                    if (message.parentElement) {
                        message.remove();
                    }
                }, 300);
            }
        }, 5000 + (index * 200));
    });
});