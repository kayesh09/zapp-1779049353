// Mobile menu toggle
document.querySelector('.mobile-menu-btn')?.addEventListener('click', function() {
    document.querySelector('.nav-links').classList.toggle('active');
});

// Auto-hide flash messages
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    });
}, 5000);

// Update cart count on page load
function updateCartCount() {
    fetch('/cart/count')
        .then(res => res.json())
        .then(data => {
            document.getElementById('cart-count').textContent = data.count;
        })
        .catch(err => console.error('Error updating cart count:', err));
}

document.addEventListener('DOMContentLoaded', updateCartCount);