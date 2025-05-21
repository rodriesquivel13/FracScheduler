function deselectAll() {
    const checkboxes = document.querySelectorAll('input[name="fractions"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

// Mostrar mensaje flotante si existe
window.addEventListener('DOMContentLoaded', () => {
    const errorDiv = document.getElementById('floating-error');
    if (errorDiv) {
        const message = errorDiv.getAttribute('data-message');
        errorDiv.textContent = message;

        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }
});