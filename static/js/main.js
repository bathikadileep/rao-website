// Auto-hide flash messages after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash').forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'all 0.3s ease';
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(100%)';
            setTimeout(() => flash.remove(), 300);
        }, 4000);
    });

    // Auto-hide navbar dropdown on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-dropdown')) {
            document.querySelectorAll('.nav-dropdown').forEach(d => d.classList.remove('active'));
        }
    });
});

// Mobile menu toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    menu.classList.toggle('active');
    document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
}

// Update cart badge count
function updateCartCount() {
    fetch('/cart/count')
        .then(res => res.json())
        .then(data => {
            const badge = document.getElementById('cart-count');
            if (badge) {
                badge.textContent = data.count;
                badge.style.display = data.count > 0 ? 'flex' : 'none';
            }
        })
        .catch(() => {});
}

document.addEventListener('DOMContentLoaded', updateCartCount);
