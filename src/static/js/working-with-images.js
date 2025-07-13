document.addEventListener('DOMContentLoaded', function () {
    const userSubscriptionPlan = window.userSubscriptionPlan;
    const allowedPlans = window.allowedPlans;

    console.log('User subscription plan:', userSubscriptionPlan);
    console.log('Allowed plans:', allowedPlans);
    console.log('Photos found:', document.querySelectorAll('.user-photo').length);

    // Функция для отображения ошибок
    function showError(message) {
        alert(message);
    }

    // Функция для проверки и показа пустого состояния
    function checkEmptyState() {
        const photosGrid = document.getElementById('photosGrid');
        const remainingPhotos = photosGrid.querySelectorAll('.user-photo');

        console.log('Remaining photos count:', remainingPhotos.length);

        if (remainingPhotos.length === 0) {
            // Удаляем старое пустое состояние если оно есть
            const existingEmptyState = photosGrid.querySelector('.empty-state');
            if (existingEmptyState) {
                existingEmptyState.remove();
            }

            // Создаем новое пустое состояние
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
            console.log('Empty state shown');
        }
    }

    // Функция для обновления счетчика фотографий
    function updatePhotoCount() {
        const photoCountElement = document.getElementById('photoCount');
        const remainingPhotos = document.querySelectorAll('.user-photo').length;

        if (photoCountElement) {
            photoCountElement.textContent = remainingPhotos;
        }
    }

    // Функция для скачивания изображения
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
            console.error('Error loading image:', url);
            showError("Error loading image for download");
        };
    }

    // Функция для проверки доступа к размеру изображения
    function canAccessSize(userPlan, requiredSize) {
        if (!userPlan) return false;

        const planHierarchy = {
            'Basic': ['200'],
            'Premium': ['200', '400', 'original'],
            'Enterprise': ['200', '400', 'original']
        };

        return planHierarchy[userPlan] && planHierarchy[userPlan].includes(requiredSize);
    }

    // Функция получения CSRF-токена
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

    // Инициализация меню скачивания и обработка событий для каждой фотки
    document.querySelectorAll('.user-photo').forEach(photo => {
        const downloadBtn = photo.querySelector('.download-btn');
        const downloadMenu = photo.querySelector('.download-menu');

        console.log('Processing photo:', photo.dataset.imageId);
        console.log('Download button found:', !!downloadBtn);
        console.log('Download menu found:', !!downloadMenu);

        if (downloadBtn && downloadMenu) {
            // Показать/скрыть меню скачивания
            downloadBtn.addEventListener('click', (e) => {
                console.log('Download button clicked');
                e.stopPropagation();

                // Закрыть другие меню
                document.querySelectorAll('.download-menu').forEach(menu => {
                    if (menu !== downloadMenu) menu.classList.remove('show');
                });

                downloadMenu.classList.toggle('show');
                console.log('Menu visibility:', downloadMenu.classList.contains('show'));
            });

            // Закрыть меню при клике вне фото
            document.addEventListener('click', (e) => {
                if (!photo.contains(e.target)) {
                    downloadMenu.classList.remove('show');
                }
            });
        }

        // Обработка доступности опций скачивания
        const downloadOptions = photo.querySelectorAll('.download-option');
        console.log('Download options found:', downloadOptions.length);

        downloadOptions.forEach(option => {
            const size = option.dataset.size;
            const format = option.dataset.format;
            const type = option.dataset.type;

            console.log('Processing option:', size, format, type);

            // Проверяем доступность опции
            let isAccessible = canAccessSize(userSubscriptionPlan, size);

            console.log('Option accessible:', isAccessible);

            if (!isAccessible) {
                option.disabled = true;
                option.style.opacity = '0.5';
                option.style.cursor = 'not-allowed';
                option.title = 'Upgrade your plan to access this option';
                option.classList.add('disabled');
            }

            // Обработчик клика по опции скачивания
            option.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                console.log('Download option clicked:', this.dataset.size, this.dataset.format);

                if (this.disabled || this.classList.contains('disabled')) {
                    showError("You need to upgrade your subscription to access this download option.");
                    return;
                }

                const imageUrl = this.dataset.url;
                const size = this.dataset.size;
                const format = this.dataset.format;
                const type = this.dataset.type;
                const imageSubscriptionPlan = this.closest('.user-photo').dataset.subscription;
                const imageId = this.closest('.user-photo').dataset.imageId;

                console.log('Download params:', {
                    imageUrl,
                    size,
                    format,
                    type,
                    imageSubscriptionPlan,
                    imageId
                });

                // Проверяем подписку пользователя
                if (!userSubscriptionPlan) {
                    showError("You need a subscription to download images. Please subscribe.");
                    return;
                }

                // Проверяем доступ к изображению
                if (allowedPlans && allowedPlans[userSubscriptionPlan]) {
                    if (!allowedPlans[userSubscriptionPlan].includes(imageSubscriptionPlan)) {
                        showError("You don't have permission to download this image. Please upgrade your subscription.");
                        return;
                    }
                }

                // Скачиваем изображение
                const title = `image_${imageId}`;
                downloadImage(imageUrl, size, userSubscriptionPlan, title, format);

                // Закрываем меню
                downloadMenu.classList.remove('show');
            });
        });

        // Delete button - ИСПРАВЛЕННАЯ ВЕРСИЯ
        const deleteBtn = photo.querySelector('.delete-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                const imageId = photo.dataset.imageId;
                console.log('Deleting image:', imageId);
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
                        // Удаляем фото
                        photo.remove();

                        // Обновляем счетчик фотографий
                        updatePhotoCount();

                        // Проверяем, нужно ли показать пустое состояние
                        checkEmptyState();

                        console.log('Image deleted successfully');
                    } else {
                        showError(data.error || 'Failed to delete image');
                    }
                })
                .catch(error => {
                    showError('Failed to delete image');
                    console.error(error);
                });
            });
        }

        // Link button (если есть)
        const linkBtn = photo.querySelector('.link-btn');
        if (linkBtn) {
            linkBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const imageId = photo.dataset.imageId;
                console.log('Creating temporary link for image:', imageId);
                // Реализуйте логику создания временной ссылки
            });
        }
    });

    // Глобальный обработчик для закрытия всех меню при клике вне них
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-photo')) {
            document.querySelectorAll('.download-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    // Закрытие меню при нажатии Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.download-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
});