# Britlearn Academy - Site Institucional

Modern responsive English school website built with PHP, JavaScript and vanilla CSS.

## Requirements

- PHP 8.2 or higher
- Apache with mod_rewrite (or Nginx with rewrite rules)
- `mail()` function enabled (for email sending - optional in Docker)

## Installation

### Local Development

```bash
cd Web-Site
docker-compose up -d
# Access: http://localhost:8080
```

### Production (Kubernetes)

```bash
# Build image
docker build -t updateinformatica/britlearnacademy-web:latest .

# Push to registry
docker push updateinformatica/britlearnacademy-web:latest

# Restart deployment
kubectl rollout restart deployment/britlearn-site-blue -n britlearn-academy-site
```

## Admin Panel

- URL: https://britlearnacademy.online/admin/
- Username: `admin`
- Password: `britlearn2026`

**Important:** Change the password in `config/config.php` after first login!

## Project Structure

```
Web-Site/
├── Dockerfile               # Build image PHP/Apache
├── docker-compose.yml       # Local development
├── config/config.php        # Site configuration
├── includes/
│   ├── functions.php        # Helper functions, CSRF, validation
│   ├── header.php           # Dynamic header template
│   ├── footer.php           # Dynamic footer template
│   └── email.php            # Email sending class
├── pages/
│   ├── home.php             # Homepage content
│   ├── story.php            # Our Story page
│   └── contact.php          # Contact page (form + phones)
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
- Email notifications for contact form & waitlist (optional - fails gracefully)
- Admin dashboard to view messages and waitlist signups
- Responsive design (mobile-friendly)
- Scroll animations
- Security headers
- BritLearn-APP button in navigation (opens in new tab)

## Configuration

### Site Settings (config/config.php)

```php
define('SITE_NAME', 'Britlearn Academy');
define('SITE_URL', 'https://britlearnacademy.online');
define('ADMIN_EMAIL', 'contact@britlearnacademy.online');
define('CONTACT_EMAIL', 'contact@britlearnacademy.online');
```

### Email Configuration

By default, emails are saved to `data/messages.json` and `data/waitlist.json`. The `mail()` function is optional and fails gracefully in Docker.

For production email, configure SMTP in `includes/email.php` or use a service like SendGrid/Mailgun.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SITE_NAME` | Site name | `Britlearn Academy` |
| `SITE_URL` | Site URL | `https://britlearnacademy.online` |
| `ADMIN_EMAIL` | Admin email | `contact@britlearnacademy.online` |
| `CONTACT_EMAIL` | Contact form email | `contact@britlearnacademy.online` |

## Kubernetes Deployment

### Namespace
- `britlearn-academy-site`

### Deployments
- `britlearn-site-blue` (active)
- `britlearn-site-green` (inactive)

### Ingress
- Host: `britlearnacademy.online`
- Path: `/` (Prefix)
- TLS: Let's Encrypt

## Security

- CSRF tokens on all forms
- Rate limiting on API endpoints
- Input validation and sanitization
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Secrets protected via `.gitignore`
