document.addEventListener('DOMContentLoaded', function () {
    // Add popup notification if not exists
    if (!document.getElementById('popup-alert')) {
        const popup = document.createElement('div');
        popup.id = 'popup-alert';
        popup.style.display = 'none';
        popup.style.position = 'fixed';
        popup.style.top = '24px';
        popup.style.right = '24px';
        popup.style.background = '#2ecc40';
        popup.style.color = 'white';
        popup.style.padding = '12px 24px';
        popup.style.borderRadius = '8px';
        popup.style.fontSize = '16px';
        popup.style.zIndex = '9999';
        popup.style.boxShadow = '0 2px 12px rgba(0,0,0,0.2)';
        document.body.appendChild(popup);
    }

    // Pretty notification
    function showSuccess(message) {
        const popup = document.getElementById('popup-alert');
        popup.textContent = message;
        popup.style.display = 'block';
        setTimeout(() => { popup.style.display = 'none'; }, 2000);
    }

    // Error display function
    function showError(message) {
        alert(message);
    }

    // Check and show empty state
    function checkEmptyState() {
        const photosGrid = document.getElementById('photosGrid');
        const remainingPhotos = photosGrid.querySelectorAll('.user-photo');

        if (remainingPhotos.length === 0) {
            const existingEmptyState = photosGrid.querySelector('.empty-state');
            if (existingEmptyState) {
                existingEmptyState.remove();
            }
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            emptyState.id = 'emptyState';
            emptyState.innerHTML = `
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
                <h3>No photos yet</h3>
                <p>Upload your first photo to get started!</p>
            `;
            photosGrid.appendChild(emptyState);
        }
    }

    // Update photo counter
    function updatePhotoCount() {
        const photoCountElement = document.getElementById('photoCount');
        const remainingPhotos = document.querySelectorAll('.user-photo').length;
        if (photoCountElement) {
            photoCountElement.textContent = remainingPhotos;
        }
    }

    // Download image function
    function downloadImage(url, size, plan, title, format) {
        const img = new Image();
        img.crossOrigin = 'Anonymous';
        img.src = url;

        img.onload = function () {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            let width = size === 'original' ? img.width : parseInt(size);
            let height = size === 'original' ? img.height : parseInt(size);
            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);
            const dataUrl = canvas.toDataURL(`image/${format}`);
            const link = document.createElement('a');
            link.href = dataUrl;
            link.download = `${title}_${size}.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };

        img.onerror = function() {
            showError("Failed to load image for download");
        };
    }

    // Check access to image size
    function canAccessSize(userPlan, requiredSize) {
        if (!userPlan) return false;
        const planHierarchy = {
            'Basic': ['200'],
            'Premium': ['200', '400', 'original'],
            'Enterprise': ['200', '400', 'original']
        };
        return planHierarchy[userPlan] && planHierarchy[userPlan].includes(requiredSize);
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initialize download menu and event handlers for each photo
    document.querySelectorAll('.user-photo').forEach(photo => {
        const downloadBtn = photo.querySelector('.download-btn');
        const downloadMenu = photo.querySelector('.download-menu');

        if (downloadBtn && downloadMenu) {
            downloadBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                document.querySelectorAll('.download-menu').forEach(menu => {
                    if (menu !== downloadMenu) menu.classList.remove('show');
                });
                downloadMenu.classList.toggle('show');
            });

            document.addEventListener('click', (e) => {
                if (!photo.contains(e.target)) {
                    downloadMenu.classList.remove('show');
                }
            });
        }

        const downloadOptions = photo.querySelectorAll('.download-option');
        downloadOptions.forEach(option => {
            const size = option.dataset.size;
            let isAccessible = canAccessSize(window.userSubscriptionPlan, size);

            if (!isAccessible) {
                option.disabled = true;
                option.style.opacity = '0.5';
                option.style.cursor = 'not-allowed';
                option.title = 'Upgrade your plan to access this option';
                option.classList.add('disabled');
            }

            option.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                if (this.disabled || this.classList.contains('disabled')) {
                    showError("You need to upgrade your subscription to use this download option.");
                    return;
                }

                const imageUrl = this.dataset.url;
                const size = this.dataset.size;
                const format = this.dataset.format;
                const type = this.dataset.type;
                const imageId = this.closest('.user-photo').dataset.imageId;

                if (!window.userSubscriptionPlan) {
                    showError("A subscription is required to download images. Please subscribe.");
                    return;
                }

                if (window.allowedPlans && window.allowedPlans[window.userSubscriptionPlan]) {
                    const imageSubscriptionPlan = this.closest('.user-photo').dataset.subscription;
                    if (!window.allowedPlans[window.userSubscriptionPlan].includes(imageSubscriptionPlan)) {
                        showError("You do not have permission to download this image. Please upgrade your subscription.");
                        return;
                    }
                }

                const title = `image_${imageId}`;
                downloadImage(imageUrl, size, window.userSubscriptionPlan, title, format);
                downloadMenu.classList.remove('show');
            });
        });

        // Delete button
        const deleteBtn = photo.querySelector('.delete-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                const imageId = photo.dataset.imageId;
                fetch('/images/delete-image/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: `image_id=${encodeURIComponent(imageId)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        photo.remove();
                        updatePhotoCount();
                        checkEmptyState();
                    } else {
                        showError(data.error || 'Failed to delete image');
                    }
                })
                .catch(error => {
                    showError('Failed to delete image');
                });
            });
        }

        // Link button (temporary link)
        const linkBtn = photo.querySelector('.link-btn');
        if (linkBtn) {
            linkBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const imageId = photo.dataset.imageId;
                const expiresInSeconds = 3600; // you can replace with prompt if desired

                linkBtn.disabled = true;
                linkBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';

                try {
                    const response = await fetch('/images/create-temporary-link/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            image_id: imageId,
                            expires_in_seconds: expiresInSeconds
                        })
                    });

                    const data = await response.json();

                    if (data.success && data.link_url) {
                        await navigator.clipboard.writeText(data.link_url);
                        showSuccess("Temporary link copied!");
                    } else {
                        showError(data.error || 'Error creating temporary link');
                    }
                } catch (err) {
                    showError('Error creating temporary link');
                } finally {
                    linkBtn.disabled = false;
                    linkBtn.innerHTML = '<i class="fa fa-link"></i>';
                }
            });
        }
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-photo')) {
            document.querySelectorAll('.download-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.download-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
});