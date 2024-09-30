document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('themeToggleButton');
    const currentTheme = localStorage.getItem('theme') || 'light';

    document.body.classList.add(`${currentTheme}-mode`);

    themeToggleButton.addEventListener('click', () => {
        if (document.body.classList.contains('light-mode')) {
            document.body.classList.remove('light-mode');
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            themeToggleButton.innerHTML = '<i class="fa-solid fa-moon"></i>';
        } else {
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
            themeToggleButton.innerHTML = '<i class="fa-solid fa-sun"></i>';
        }
    });
});