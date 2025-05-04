document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const outdoorBtn = document.getElementById('outdoor-btn');
    const indoorBtn = document.getElementById('indoor-btn');
    const contactsBtn = document.getElementById('contacts-btn');
    const backBtn = document.getElementById('back-btn');
    const contentArea = document.getElementById('content-area');
    const searchInput = document.querySelector('.search-form input');
    let previousSection = 'outdoor-plants';

    // Функция для показа секции
    function showSection(sectionId) {
        const sections = contentArea.querySelectorAll('.content-section');
        sections.forEach(section => section.classList.remove('active'));
        document.getElementById(sectionId).classList.add('active');
        if (sectionId !== 'product-detail') {
            previousSection = sectionId;
        }
    }

    // Обработчики кнопок меню
    outdoorBtn.addEventListener('click', () => showSection('outdoor-plants'));
    indoorBtn.addEventListener('click', () => showSection('indoor-plants'));
    contactsBtn.addEventListener('click', () => showSection('contacts'));
    backBtn.addEventListener('click', () => showSection(previousSection));

    // Обработчик кликов по карточкам товаров
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.classList.contains('add-btn') || e.target.closest('.add-btn')) {
                return;
            }
            const name = this.dataset.name;
            const description = this.dataset.description;
            const gallery = JSON.parse(this.dataset.gallery || '[]');
            const addUrl = this.dataset.addUrl;
            document.getElementById('detail-name').textContent = name;
            document.getElementById('detail-description').textContent = description;
            const galleryContainer = document.getElementById('detail-gallery');
            galleryContainer.innerHTML = gallery.length
                ? gallery.map(url => `<img src="${url}" alt="${name}">`).join('')
                : '<p>Галерея пуста.</p>';
            const addForm = document.getElementById('add-to-cart-form');
            addForm.action = addUrl;
            showSection('product-detail');
        });
    });

    // Обработчик добавления в корзину через AJAX
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Товар добавлен в корзину!');
                } else {
                    alert('Ошибка при добавлении в корзину.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка. Попробуйте снова.');
            });
        });
    });

    // Клиентский поиск
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();
        const allCards = document.querySelectorAll('.product-card');
        allCards.forEach(card => {
            const name = card.dataset.name.toLowerCase();
            card.style.display = name.includes(query) ? 'flex' : 'none';
        });
    });

    // Показать уличные растения по умолчанию
    showSection('outdoor-plants');
});