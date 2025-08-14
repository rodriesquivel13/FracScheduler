function deselectAll() {
    const checkboxes = document.querySelectorAll('input[name="fractions"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

// Tooltip global único
let tooltip;

window.addEventListener('DOMContentLoaded', () => {
    console.log("scripts.js cargado correctamente");

    // Mostrar mensaje flotante si existe
    const errorDiv = document.getElementById('floating-error');
    if (errorDiv) {
        const message = errorDiv.getAttribute('data-message');
        errorDiv.textContent = message;
        setTimeout(() => errorDiv.remove(), 3000);
    }

    // Crear tooltip global y añadir al body
    tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.style.position = 'fixed';
    tooltip.style.top = '0';
    tooltip.style.left = '0';
    tooltip.style.opacity = '0';
    tooltip.style.visibility = 'hidden';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.zIndex = '9999';
    document.body.appendChild(tooltip);

    const dates = document.querySelectorAll('.date-circle[data-tooltip]');
    dates.forEach(el => {
        el.addEventListener('mouseenter', () => {
            tooltip.textContent = el.getAttribute('data-tooltip');
            tooltip.style.visibility = 'visible';
            tooltip.style.opacity = '1';
        });

        el.addEventListener('mousemove', (event) => {
            const padding = 10;
            let x = event.clientX;
            let y = event.clientY - 40; // un poco arriba del cursor

            const tooltipRect = tooltip.getBoundingClientRect();
            const screenWidth = window.innerWidth;
            const screenHeight = window.innerHeight;

            if (x + tooltipRect.width + padding > screenWidth) {
                x = screenWidth - tooltipRect.width - padding;
            }
            if (y - tooltipRect.height - padding < 0) {
                y = event.clientY + 20; // si no cabe arriba, poner debajo
            }

            tooltip.style.transform = `translate(${x}px, ${y}px)`;
        });

        el.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
            tooltip.style.visibility = 'hidden';
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.getElementById('hamburger-btn');
  const sidebar = document.getElementById('sidebar');
  const body = document.body;

  hamburger.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    hamburger.classList.toggle('active');
    body.classList.toggle('sidebar-open');
  });

  // Opcional: cerrar sidebar con tecla ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === "Escape" && sidebar.classList.contains('active')) {
      sidebar.classList.remove('active');
      hamburger.classList.remove('active');
      body.classList.remove('sidebar-open');
    }
  });
});