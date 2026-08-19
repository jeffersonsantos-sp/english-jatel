<section class="page-hero contact-hero">
<div class="container">
<span class="eyebrow">CONTACT US</span>
<h1>Let's start your <span>English journey.</span></h1>
<p>Tell us about your goals and we will help you find the right learning path.</p>
</div>
</section>

<section class="contact-section section">
<div class="container contact-grid">
<div class="contact-info">
<span class="eyebrow">GET IN TOUCH</span>
<h2>We would love to <span>hear from you.</span></h2>
<p>Whether you are interested in our English courses, the Britlearn App or a partnership, our team is ready to help.</p>
<div class="contact-item"><span>📍</span><div><strong>Our London Office</strong><p>London, United Kingdom</p></div></div>
<div class="contact-item"><span>✉️</span><div><strong>Email us</strong><p><?= CONTACT_EMAIL ?></p></div></div>
<div class="contact-item"><span>🌎</span><div><strong>Global Learning</strong><p>Students from around the world</p></div></div>
</div>

<form class="contact-form" id="contactForm">
<?= csrfField() ?>
<div class="form-row">
<div><label for="firstName">First Name</label><input type="text" id="firstName" name="firstName" required></div>
<div><label for="lastName">Last Name</label><input type="text" id="lastName" name="lastName" required></div>
</div>
<label for="email">Email Address</label>
<input type="email" id="email" name="email" required>
<label for="interest">What are you interested in?</label>
<select id="interest" name="interest">
<option>English Courses</option>
<option>Britlearn App</option>
<option>Business English</option>
<option>Partnership</option>
<option>Other</option>
</select>
<label for="message">Your Message</label>
<textarea id="message" name="message" rows="6" placeholder="Tell us about your English learning goals..." required></textarea>
<button type="submit" class="btn btn-primary full-width">Send Message →</button>
<p class="form-message" id="contactMessage"></p>
</form>
</div>
</section>
