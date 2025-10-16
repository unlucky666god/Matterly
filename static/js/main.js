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
    document.getElementById('customOrderModal').style.display = 'block';
}

function closeCustomOrderModal() {
    document.getElementById('customOrderModal').style.display = 'none';
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('customOrderModal');
    if (event.target === modal) {
        closeCustomOrderModal();
    }
}

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

    const orderData = {
        fullName: formData.get('fullName'),
        phone: formData.get('phone'),
        email: formData.get('email'),
        telegram: formData.get('telegram'),
        orderDescription: formData.get('orderDescription')
    };

    try {
        // Показываем индикатор загрузки
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Отправка...';
        submitBtn.disabled = true;

        // Отправляем данные на сервер
        const response = await fetch('/api/custom-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            // Показываем сообщение об успехе
            alert('✅ Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.');
            form.reset();
            closeCustomOrderModal();
        } else {
            throw new Error('Ошибка при отправке заявки');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('❌ Произошла ошибка при отправке заявки. Пожалуйста, попробуйте еще раз или свяжитесь с нами напрямую.');
    } finally {
        // Восстанавливаем кнопку
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Отправить заявку';
            submitBtn.disabled = false;
        }
    }
}