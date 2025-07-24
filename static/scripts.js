function deselectAll() {
    const checkboxes = document.querySelectorAll('input[name="fractions"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

// Mostrar mensaje flotante si existe
window.addEventListener('DOMContentLoaded', () => {
    console.log("scripts.js cargado correctamente");

    const errorDiv = document.getElementById('floating-error');
    if (errorDiv) {
        const message = errorDiv.getAttribute('data-message');
        errorDiv.textContent = message;

        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }

    // TOOLTIP: Agrega tooltips a los días con atributo data-tooltip
    const dates = document.querySelectorAll('.date-circle[data-tooltip]');
    dates.forEach(el => {
        const tooltipText = el.getAttribute('data-tooltip');
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        el.appendChild(tooltip);

        el.addEventListener('mouseenter', () => {
            tooltip.style.opacity = '1';
        });
        el.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
        });
    });
});
