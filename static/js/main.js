document.addEventListener('DOMContentLoaded', () => {
    const logo = document.getElementById('logo-animated');
    if (logo) {
        const text = logo.textContent;
        logo.innerHTML = '';
        text.split('').forEach((char, i) => {
            const span = document.createElement('span');
            span.textContent = char === ' ' ? '\u00A0' : char;
            span.style.display = 'inline-block';
            span.style.opacity = '0';
            span.style.transform = 'translateY(20px)';
            logo.appendChild(span);
            gsap.to(span, {
                opacity: 1,
                y: 0,
                delay: i * 0.05,
                duration: 0.5,
                ease: "power3.out"
            });
        });
    }

    const menuButton = document.getElementById('mobile-menu-button');
    const closeMenu = document.getElementById('close-menu');
    const mobileMenu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-menu-overlay');

    if (!menuButton || !mobileMenu || !overlay) return;

    const openMenu = () => {
        mobileMenu.classList.remove('translate-x-full');
        mobileMenu.classList.add('translate-x-0');
        overlay.classList.remove('pointer-events-none', 'opacity-0');
        overlay.classList.add('opacity-100');
        document.body.classList.add('overflow-hidden');
        menuButton.classList.add('burger-active');
    };

    const closeMenuHandler = () => {
        mobileMenu.classList.remove('translate-x-0');
        mobileMenu.classList.add('translate-x-full');
        overlay.classList.remove('opacity-100');
        overlay.classList.add('pointer-events-none', 'opacity-0');
        document.body.classList.remove('overflow-hidden');
        menuButton.classList.remove('burger-active');
    };

    menuButton.addEventListener('click', openMenu);
    closeMenu.addEventListener('click', closeMenuHandler);
    overlay.addEventListener('click', closeMenuHandler);
    mobileMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenuHandler));
});

// Функции для модального окна индивидуального заказа
function openCustomOrderModal() {
    const modal = document.getElementById('customOrderModal');
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    
    // Фокус на первое поле после анимации
    setTimeout(() => {
        const firstInput = modal.querySelector('input');
        if (firstInput) firstInput.focus();
    }, 300);
}

function closeCustomOrderModal() {
    const modal = document.getElementById('customOrderModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
    
    // Сбрасываем фокус для скрытия мобильной клавиатуры
    if (document.activeElement) {
        document.activeElement.blur();
    }
}

// Закрытие модального окна при клике вне его
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('customOrderModal');
    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === this) {
                closeCustomOrderModal();
            }
        });
    }
});

// Закрытие на Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeCustomOrderModal();
    }
});

// Предотвращаем закрытие при клике на форму
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('customOrderForm');
    if (form) {
        form.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
});

// Обработка формы индивидуального заказа
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('customOrderForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitCustomOrder();
        });
    }
});

// Функция отправки индивидуального заказа
async function submitCustomOrder() {
    const form = document.getElementById('customOrderForm');
    const formData = new FormData(form);

    // Валидация обязательных полей
    const requiredFields = ['fullName', 'phone', 'email', 'orderDescription'];
    let isValid = true;
    
    requiredFields.forEach(field => {
        const input = form.querySelector(`[name="${field}"]`);
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('border-red-500');
        } else {
            input.classList.remove('border-red-500');
        }
    });

    if (!isValid) {
        alert('⚠️ Пожалуйста, заполните все обязательные поля');
        return;
    }

    const orderData = {
        fullName: formData.get('fullName').trim(),
        phone: formData.get('phone').trim(),
        email: formData.get('email').trim(),
        telegram: formData.get('telegram').trim(),
        orderDescription: formData.get('orderDescription').trim()
    };

    try {
        // Показываем индикатор загрузки
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-70');

        // Отправляем данные на сервер
        const response = await fetch('/api/custom-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            // Показываем красивый toast вместо alert
            showToast('✅ Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.', 'success');
            form.reset();
            closeCustomOrderModal();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Ошибка при отправке заявки');
        }

    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Произошла ошибка при отправке заявки. Пожалуйста, попробуйте еще раз.', 'error');
    } finally {
        // Восстанавливаем кнопку
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Отправить заявку';
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-70');
        }
    }
}

// Функция для показа красивых уведомлений
function showToast(message, type = 'info') {
    // Создаем элемент тоста
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-xl backdrop-blur-sm border transition-all transform translate-x-0 opacity-100 ${
        type === 'success' 
            ? 'bg-green-500/10 border-green-500/20 text-green-400' 
            : 'bg-red-500/10 border-red-500/20 text-red-400'
    }`;
    toast.textContent = message;
    
    // Добавляем в DOM
    document.body.appendChild(toast);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
    
    // Закрытие по клику
    toast.addEventListener('click', () => {
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    });
}

// Оптимизация для мобильных устройств
document.addEventListener('DOMContentLoaded', function() {
    // Предотвращаем масштабирование при фокусе на iOS
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.fontSize = '16px'; // Предотвращает зум на iOS
        });
    });
    
    // Улучшаем обработку виртуальной клавиатуры
    if ('visualViewport' in window) {
        const visualViewport = window.visualViewport;
        visualViewport.addEventListener('resize', function() {
            // Корректируем позицию модального окна при появлении клавиатуры
            const modal = document.getElementById('customOrderModal');
            if (!modal.classList.contains('hidden')) {
                modal.style.top = `${visualViewport.offsetTop}px`;
                modal.style.height = `${visualViewport.height}px`;
            }
        });
    }
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom order modal initialized');
});