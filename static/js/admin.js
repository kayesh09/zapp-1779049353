// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
});

function initializeAdmin() {
    loadDashboardStats();
    initializeDataTables();
    initializeCharts();
}

function loadDashboardStats() {
    fetch('/admin/api/stats?days=30')
        .then(response => response.json())
        .then(data => {
            drawChart(data);
        })
        .catch(error => console.error('Error loading stats:', error));
}

function drawChart(data) {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;

    const canvas = ctx.getContext('2d');

    // Simple chart implementation (you can use Chart.js library)
    console.log('Chart data:', data);
    // This would require Chart.js library to be included
}

function initializeDataTables() {
    // Initialize any data tables with sorting/filtering
    const tables = document.querySelectorAll('[data-table]');
    tables.forEach(table => {
        // Add sorting functionality
        const headers = table.querySelectorAll('th');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, headers.indexOf(this));
            });
        });
    });
}

function sortTable(table, columnIndex) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isAscending = !table.dataset.sortAsc;

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent;
        const bValue = b.cells[columnIndex].textContent;

        if (!isNaN(aValue) && !isNaN(bValue)) {
            return isAscending ? aValue - bValue : bValue - aValue;
        }

        if (isAscending) {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });

    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));

    table.dataset.sortAsc = isAscending;
}

function initializeCharts() {
    // Initialize any charts (requires Chart.js library)
    console.log('Charts initialized');
}

function deleteItem(itemId, itemType) {
    if (!confirm(`Are you sure you want to delete this ${itemType}?`)) {
        return;
    }

    fetch(`/admin/${itemType}/${itemId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`${itemType} deleted successfully`, 'success');
            setTimeout(() => location.reload(), 1000);
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateOrderStatus(orderId, newStatus) {
    fetch(`/admin/order/${orderId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Order status updated', 'success');
            setTimeout(() => location.reload(), 1000);
        }
    })
    .catch(error => console.error('Error:', error));
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(() => alertDiv.remove(), 5000);
}

// Export for use in HTML
window.deleteItem = deleteItem;
window.updateOrderStatus = updateOrderStatus;