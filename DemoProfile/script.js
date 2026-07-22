const chips = document.querySelectorAll('.chip');
const revealTargets = document.querySelectorAll('.hero-copy, .profile-card, .panel');

revealTargets.forEach((element, index) => {
  element.classList.add('fade-in');
  element.style.animationDelay = `${index * 90}ms`;
});

chips.forEach((chip) => {
  chip.addEventListener('click', () => {
    chip.classList.toggle('active');
  });
});
