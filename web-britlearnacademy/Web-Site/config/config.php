<?php
define('SITE_NAME', 'Britlearn Academy');
define('SITE_URL', 'https://britlearnacademy.online');
define('ADMIN_EMAIL', 'updateinformatica2023@gmail.com');
define('CONTACT_EMAIL', 'updateinformatica2023@gmail.com');

define('BASE_PATH', dirname(__DIR__));
define('DATA_PATH', BASE_PATH . '/data');
define('ASSETS_URL', 'assets');

define('CSRF_TOKEN_NAME', 'csrf_token');
define('SESSION_LIFETIME', 3600 * 4);

define('ADMIN_USER', 'admin');
define('ADMIN_PASS_HASH', password_hash('britlearn2026', PASSWORD_DEFAULT));

define('RATE_LIMIT_MAX', 5);
define('RATE_LIMIT_WINDOW', 300);

if (session_status() === PHP_SESSION_NONE) {
    session_set_cookie_params([
        'lifetime' => SESSION_LIFETIME,
        'path' => '/',
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
    session_start();
}

if (!is_dir(DATA_PATH)) {
    mkdir(DATA_PATH, 0755, true);
}

header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
header('X-XSS-Protection: 1; mode=block');
header('Referrer-Policy: strict-origin-when-cross-origin');
