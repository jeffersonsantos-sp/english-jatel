# Britlearn Academy

Modern responsive English school website built with PHP, JavaScript and vanilla CSS.

## Requirements

- PHP 7.4 or higher
- Apache with mod_rewrite (or Nginx with rewrite rules)
- `mail()` function enabled (for email sending)

## Installation

1. Copy all files to your web server's document root (e.g., `htdocs/britlearnacademy/`)
2. Enable mod_rewrite on Apache:
   ```bash
   sudo a2enmod rewrite
   sudo systemctl restart apache2
   ```
3. Ensure `data/` directory is writable by the web server:
   ```bash
   chmod 755 data/
   ```
4. Access the site at `http://your-server/britlearnacademy/`

## Admin Panel

- URL: `http://your-server/britlearnacademy/admin/`
- Username: `admin`
- Password: `britlearn2026`

**Important:** Change the password in `config/config.php` after first login!

## Project Structure

```
britlearnacademy/
├── config/config.php        # Site configuration
├── includes/
│   ├── functions.php        # Helper functions, CSRF, validation
│   ├── header.php           # Dynamic header template
│   ├── footer.php           # Dynamic footer template
│   └── email.php            # Email sending class
├── pages/
│   ├── home.php             # Homepage content
│   ├── story.php            # Our Story page
│   └── contact.php          # Contact page
├── api/
│   ├── contact.php          # Contact form API
│   ├── waitlist.php         # Waitlist signup API
│   └── auth.php             # Authentication API
├── admin/
│   ├── login.php            # Admin login
│   ├── index.php            # Admin dashboard
│   ├── messages.php         # Mark messages as read
│   └── logout.php           # Admin logout
├── assets/
│   ├── css/style.css        # Stylesheet
│   ├── js/script.js         # JavaScript
│   └── imagens/             # Images
├── data/                    # Auto-created, stores messages & waitlist
├── index.php                # Main router
└── .htaccess                # URL rewriting
```

## Features

- PHP routing with clean URLs
- CSRF protection on all forms
- Server-side + client-side form validation
- Rate limiting on API endpoints
- Email notifications for contact form & waitlist
- Admin dashboard to view messages and waitlist signups
- Responsive design (mobile-friendly)
- Scroll animations
- Security headers

## Email Configuration

By default, emails are sent using PHP's `mail()` function. For production, consider configuring SMTP in `includes/email.php` or using a service like SendGrid/Mailgun.
