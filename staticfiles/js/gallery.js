// plant_shop/static/js/catalog.js
document.addEventListener('DOMContentLoaded', () => {
    const miniCards = document.querySelectorAll('.mini-card');
    const productDetails = document.querySelectorAll('.product-details');

    miniCards.forEach(card => {
        card.addEventListener('click', () => {
            // Удаляем активный класс у всех карточек
            miniCards.forEach(c => c.classList.remove('active'));
            productDetails.forEach(p => p.classList.remove('active'));

            // Добавляем активный класс выбранной карточке
            card.classList.add('active');
            const productId = card.getAttribute('data-product-id');
            const targetDetail = document.getElementById(`product-${productId}`);
            if (targetDetail) {
                targetDetail.classList.add('active');
            }
        });
    });
});