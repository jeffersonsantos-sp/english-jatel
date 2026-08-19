document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menuToggle");
  const navLinks = document.getElementById("navLinks");
  if (menuToggle && navLinks) menuToggle.addEventListener("click", () => navLinks.classList.toggle("open"));

  document.querySelectorAll("#year").forEach(year => year.textContent = new Date().getFullYear());

  const launchForm = document.getElementById("launchForm");
  const launchMessage = document.getElementById("launchMessage");
  if (launchForm) launchForm.addEventListener("submit", event => {
    event.preventDefault();
    const email = document.getElementById("launchEmail").value;
    launchMessage.textContent = `Thank you! ${email} has been added to the Britlearn App waitlist. 🚀`;
    launchForm.reset();
  });

  const contactForm = document.getElementById("contactForm");
  const contactMessage = document.getElementById("contactMessage");
  if (contactForm) contactForm.addEventListener("submit", event => {
    event.preventDefault();
    const firstName = document.getElementById("firstName").value;
    contactMessage.textContent = `Thank you, ${firstName}! Your message has been sent successfully. We will contact you soon. 🇬🇧`;
    contactForm.reset();
  });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll(".course-card, .testimonial-grid article, .story-content").forEach(element => {
      element.style.opacity = "0";
      element.style.transform = "translateY(30px)";
      element.style.transition = "all 0.7s ease";
      observer.observe(element);
    });
  }
});