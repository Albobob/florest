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
        if (!contentArea) return;
        const sections = contentArea.querySelectorAll('.content-section');
        sections.forEach(section => section.classList.remove('active'));
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        if (sectionId !== 'product-detail') {
            previousSection = sectionId;
        }
    }

    // Обработчики кнопок меню
    if (outdoorBtn) outdoorBtn.addEventListener('click', () => showSection('outdoor-plants'));
    if (indoorBtn) indoorBtn.addEventListener('click', () => showSection('indoor-plants'));
    if (contactsBtn) contactsBtn.addEventListener('click', () => showSection('contacts'));
    if (backBtn) backBtn.addEventListener('click', () => showSection(previousSection));

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
            const detailName = document.getElementById('detail-name');
            const detailDescription = document.getElementById('detail-description');
            const galleryContainer = document.getElementById('detail-gallery');
            const addForm = document.getElementById('add-to-cart-form');
            if (detailName) detailName.textContent = name;
            if (detailDescription) detailDescription.textContent = description;
            if (galleryContainer) {
                galleryContainer.innerHTML = gallery.length
                    ? gallery.map(url => `<img src="${url}" alt="${name}">`).join('')
                    : '<p>Галерея пуста.</p>';
            }
            if (addForm) addForm.action = addUrl;
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
                if (data.status === 'success') {
                    alert('Товар добавлен в корзину!');
                    updateCartCount(data.cart_count);
                } else {
                    alert('Ошибка при добавлении в корзину: ' + (data.message || ''));
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка. Попробуйте снова.');
            });
        });
    });

    // Обработчик изменения количества и удаления товара в корзине
    const cartContainer = document.getElementById('cart-container');
    if (cartContainer) {
        cartContainer.addEventListener('click', function(e) {
            // Удаление товара
            if (e.target.classList.contains('remove-btn')) {
                const productId = e.target.dataset.productId;
                updateCart(productId, 0);
            }
            // Увеличение/уменьшение количества
            if (e.target.classList.contains('qty-btn')) {
                const productId = e.target.dataset.productId;
                const input = document.getElementById(`qty-input-${productId}`);
                let quantity = parseInt(input.value);
                if (e.target.classList.contains('plus')) {
                    quantity += 1;
                } else if (e.target.classList.contains('minus') && quantity > 1) {
                    quantity -= 1;
                }
                updateCart(productId, quantity);
            }
        });
    }

    function updateCart(productId, quantity) {
        fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ item_id: productId, quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateCartCount(data.cart_count);
                // Если корзина пуста, перезагрузить страницу для отображения пустой корзины
                if (data.cart_count === 0) {
                    location.reload();
                } else {
                    // Обновить количество и сумму на странице без перезагрузки (по желанию)
                    const input = document.getElementById(`qty-input-${productId}`);
                    if (input) input.value = quantity;
                    // Можно добавить обновление суммы и других элементов
                }
            } else {
                alert('Ошибка при обновлении корзины: ' + (data.message || ''));
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка. Попробуйте снова.');
        });
    }

    function updateCartCount(count) {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = count;
        }
    }

    // Клиентский поиск
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            const allCards = document.querySelectorAll('.product-card');
            allCards.forEach(card => {
                const name = card.dataset.name.toLowerCase();
                card.style.display = name.includes(query) ? 'flex' : 'none';
            });
        });
    }

    // Показать уличные растения по умолчанию
    showSection('outdoor-plants');

    // Вспомогательная функция для получения cookie
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
});