document.addEventListener('DOMContentLoaded', function() {
    // Enable all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-close alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Confirm deletion dialogs
    document.querySelectorAll('.confirm-delete').forEach(function(element) {
        element.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Print button functionality
    document.querySelectorAll('.btn-print').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
    
    // ISBN validation
    document.querySelectorAll('input[name="isbn"]').forEach(function(input) {
        input.addEventListener('blur', function() {
            const isbn = this.value.replace(/[-\s]/g, '');
            if (isbn.length !== 10 && isbn.length !== 13) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });
    
    // Due date highlighting
    document.querySelectorAll('.due-date').forEach(function(element) {
        const dueDate = new Date(element.dataset.date);
        const today = new Date();
        
        if (dueDate < today) {
            element.classList.add('overdue');
        }
    });
});