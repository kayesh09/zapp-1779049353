document.querySelectorAll('.update-cart').forEach(button => {
    button.addEventListener('click', function() {
        const cartItem = this.closest('.cart-item');
        const itemId = cartItem.dataset.itemId;
        const input = cartItem.querySelector('.qty-input');
        let quantity = parseInt(input.value);
        
        if (this.dataset.action === 'increase') {
            quantity++;
        } else if (this.dataset.action === 'decrease') {
            quantity--;
        }
        
        if (quantity < 1) quantity = 1;
        
        const formData = new FormData();
        formData.append('quantity', quantity);
        
        fetch(`/cart/update/${itemId}`, {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            
            input.value = quantity;
            cartItem.querySelector('.item-total strong').textContent = 
                `$${data.item_total.toFixed(2)}`;
            document.getElementById('cart-subtotal').textContent = 
                `$${data.cart_total.toFixed(2)}`;
            document.getElementById('cart-total').textContent = 
                `$${data.cart_total.toFixed(2)}`;
            document.getElementById('cart-count').textContent = data.cart_count;
        })
        .catch(err => console.error('Error:', err));
    });
});