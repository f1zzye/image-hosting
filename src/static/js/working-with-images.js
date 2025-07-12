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

    // Инициализация меню скачивания
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

        // Delete button
        const deleteBtn = photo.querySelector('.delete-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                const imageId = photo.dataset.imageId;
                if (confirm('Are you sure you want to delete this photo?')) {
                    console.log('Deleting image:', imageId);
                    // Реализуйте логику удаления
                }
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