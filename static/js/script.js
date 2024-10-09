document.addEventListener('DOMContentLoaded', () => {
    const profileImage = document.getElementById('profile-image');

    if (profileImage) {
        profileImage.addEventListener('mouseover', () => {
            profileImage.style.transition = 'transform 0.3s ease';
            profileImage.style.transform = 'scale(1.1)';
        });

        profileImage.addEventListener('mouseout', () => {
            profileImage.style.transition = 'transform 0.3s ease';
            profileImage.style.transform = 'scale(1)';
        });
    }

    const navLinks = document.querySelectorAll('.nav-links li a');

    navLinks.forEach(link => {
        link.addEventListener('mouseover', () => {
            link.style.transition = 'color 0.3s';
            link.style.color = '#00ffff';
        });

        link.addEventListener('mouseout', () => {
            link.style.color = '#ffffff';
        });
    });

    const skillsListItems = document.querySelectorAll('.skills-list li');
    skillsListItems.forEach(item => {
        item.addEventListener('mouseover', () => {
            item.style.transition = 'color 0.3s';
            item.style.color = '#00ffff';
        });

        item.addEventListener('mouseout', () => {
            item.style.color = '#000000';
        });
    });
});
