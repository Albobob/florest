// Функция для отображения уведомлений
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.className = `toast ${type}`;
    toast.querySelector('.toast-content').textContent = message;
    toast.style.display = 'block';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// Функция для обновления счетчика корзины
function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

// Функция для добавления товара в корзину
async function addToCart(productId) {
    try {
        const response = await fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            showToast(data.message);
            updateCartCount(data.cart_count);
        } else {
            showToast(data.message || 'Ошибка добавления в корзину', 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showToast('Ошибка добавления в корзину', 'error');
    }
}

// Инициализация обработчиков событий
document.addEventListener('DOMContentLoaded', function() {
    // Обработчик для кнопок добавления в корзину
    document.querySelectorAll('.add-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = button.dataset.productId;
            addToCart(productId);
        });
    });
}); 