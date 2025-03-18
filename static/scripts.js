function deselectAll() {
    const checkboxes = document.querySelectorAll('input[name="fractions"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}