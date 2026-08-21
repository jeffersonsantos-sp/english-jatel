<?php if ($activePage !== 'story' && $activePage !== 'contact'): ?>
<footer>
<div class="container footer-grid">
<div>
<a href="/" class="footer-logo">🇬🇧 <?= SITE_NAME ?></a>
<p>Helping learners communicate confidently since 2001.</p>
</div>
<div>
<h4>Academy</h4>
<a href="/#courses">Courses</a>
<a href="/story">Our Story</a>
<a href="/#app">Britlearn App</a>
</div>
<div>
<h4>Contact</h4>
<a href="/contact">Get in touch</a>
<a href="mailto:<?= CONTACT_EMAIL ?>"><?= CONTACT_EMAIL ?></a>
</div>
<div>
<h4>Follow us</h4>
<div class="socials">
<a href="#">Instagram</a>
<a href="#">LinkedIn</a>
<a href="#">YouTube</a>
</div>
</div>
</div>
<div class="container footer-bottom">
<span>&copy; <span class="year"></span> <?= SITE_NAME ?>. All rights reserved.</span>
<span>London, United Kingdom 🇬🇧</span>
</div>
</footer>
<?php else: ?>
<footer>
<div class="container footer-bottom">
<span>&copy; <span class="year"></span> <?= SITE_NAME ?>. All rights reserved.</span>
<span>London, United Kingdom 🇬🇧</span>
</div>
</footer>
<?php endif; ?>
<script src="<?= ASSETS_URL ?>/js/script.js"></script>
</body>
</html>
