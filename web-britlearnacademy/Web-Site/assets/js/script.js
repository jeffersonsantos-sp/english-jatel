document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menuToggle");
  const navLinks = document.getElementById("navLinks");
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
  }

  document.querySelectorAll(".year").forEach(el => el.textContent = new Date().getFullYear());
  document.querySelectorAll("#year").forEach(el => el.textContent = new Date().getFullYear());

  function showError(field, message) {
    clearError(field);
    field.style.borderColor = '#dc2626';
    const err = document.createElement('small');
    err.className = 'field-error';
    err.style.color = '#dc2626';
    err.style.fontSize = '13px';
    err.style.marginTop = '4px';
    err.style.display = 'block';
    err.textContent = message;
    field.parentNode.appendChild(err);
  }

  function clearError(field) {
    field.style.borderColor = '';
    const existing = field.parentNode.querySelector('.field-error');
    if (existing) existing.remove();
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;
    const input = document.querySelector('input[name="csrf_token"]');
    return input ? input.value : '';
  }

  const launchForm = document.getElementById("launchForm");
  const launchMessage = document.getElementById("launchMessage");
  if (launchForm) {
    const launchEmail = document.getElementById("launchEmail");
    if (launchEmail) {
      launchEmail.addEventListener('blur', () => {
        clearError(launchEmail);
        if (launchEmail.value && !validateEmail(launchEmail.value)) {
          showError(launchEmail, 'Please enter a valid email address.');
        }
      });
    }

    launchForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const email = launchEmail.value.trim();
      launchMessage.textContent = '';
      launchMessage.style.color = '';

      clearError(launchEmail);
      if (!email) {
        showError(launchEmail, 'Email is required.');
        return;
      }
      if (!validateEmail(email)) {
        showError(launchEmail, 'Please enter a valid email address.');
        return;
      }

      const submitBtn = launchForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Joining...';
      submitBtn.disabled = true;

      try {
        const formData = new FormData(launchForm);
        const res = await fetch('/api/waitlist.php', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        if (data.success) {
          launchMessage.textContent = data.message;
          launchMessage.style.color = '#16a34a';
          launchForm.reset();
        } else {
          launchMessage.textContent = data.error || 'Something went wrong. Please try again.';
          launchMessage.style.color = '#dc2626';
        }
      } catch (err) {
        launchMessage.textContent = 'Connection error. Please check your internet and try again.';
        launchMessage.style.color = '#dc2626';
      }

      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    });
  }

  const contactForm = document.getElementById("contactForm");
  const contactMessage = document.getElementById("contactMessage");
  if (contactForm) {
    const fields = {
      firstName: document.getElementById("firstName"),
      lastName: document.getElementById("lastName"),
      email: document.getElementById("email"),
      message: document.getElementById("message")
    };

    Object.entries(fields).forEach(([name, field]) => {
      if (!field) return;
      field.addEventListener('blur', () => {
        clearError(field);
        const val = field.value.trim();
        if (!val && field.required) {
          showError(field, 'This field is required.');
        } else if (name === 'email' && val && !validateEmail(val)) {
          showError(field, 'Please enter a valid email address.');
        } else if (name === 'firstName' && val.length > 100) {
          showError(field, 'First name is too long.');
        } else if (name === 'lastName' && val.length > 100) {
          showError(field, 'Last name is too long.');
        } else if (name === 'message' && val.length > 5000) {
          showError(field, 'Message is too long (max 5000 characters).');
        }
      });
    });

    contactForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      contactMessage.textContent = '';
      contactMessage.style.color = '';

      let valid = true;
      Object.entries(fields).forEach(([name, field]) => {
        if (!field) return;
        clearError(field);
        const val = field.value.trim();
        if (!val && field.required) {
          showError(field, 'This field is required.');
          valid = false;
        } else if (name === 'email' && val && !validateEmail(val)) {
          showError(field, 'Please enter a valid email address.');
          valid = false;
        }
      });

      if (!valid) return;

      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Sending...';
      submitBtn.disabled = true;

      try {
        const formData = new FormData(contactForm);
        const res = await fetch('/api/contact.php', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        if (data.success) {
          contactMessage.textContent = data.message;
          contactMessage.style.color = '#16a34a';
          contactForm.reset();
        } else {
          contactMessage.textContent = data.error || 'Something went wrong. Please try again.';
          contactMessage.style.color = '#dc2626';
        }
      } catch (err) {
        contactMessage.textContent = 'Connection error. Please check your internet and try again.';
        contactMessage.style.color = '#dc2626';
      }

      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    });
  }

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
