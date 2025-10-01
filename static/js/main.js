document.addEventListener("DOMContentLoaded", function () {
    // Анимация при прокрутке
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    });

    document.querySelectorAll('.tile, .btn').forEach(el => {
        observer.observe(el);
    });

    // Поиск
    const searchInput = document.getElementById('search');
    searchInput.addEventListener('input', function () {
        const q = this.value;
        fetch(`/search?q=${q}`)
            .then(response => response.json())
            .then(data => console.log(data)); // можно вывести результаты
    });

    // Форма обратного звонка
    document.getElementById('callback-form').addEventListener('submit', function (e) {
        e.preventDefault();
        alert('Заявка отправлена!');
    });
});