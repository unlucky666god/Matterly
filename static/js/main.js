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