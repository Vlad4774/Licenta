document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('profileToggle');
    const menu = document.getElementById('profileMenu');
    const wrapper = document.querySelector('.saleshub-profile-wrapper');

    toggle.addEventListener('click', function (e) {
        e.stopPropagation();
        wrapper.classList.toggle('open');
    });

    document.addEventListener('click', function (e) {
        if (!wrapper.contains(e.target)) {
            wrapper.classList.remove('open');
        }
    });
});
