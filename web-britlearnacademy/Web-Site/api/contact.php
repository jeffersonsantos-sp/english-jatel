<?php
require_once __DIR__ . '/../includes/functions.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonResponse(['error' => 'Method not allowed'], 405);
}

if (!verifyCsrfToken()) {
    jsonResponse(['error' => 'Invalid security token. Please refresh the page.'], 403);
}

$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
if (isRateLimited('contact_' . $ip)) {
    jsonResponse(['error' => 'Too many requests. Please try again later.'], 429);
}

$firstName = trim($_POST['firstName'] ?? '');
$lastName = trim($_POST['lastName'] ?? '');
$email = trim($_POST['email'] ?? '');
$interest = trim($_POST['interest'] ?? '');
$message = trim($_POST['message'] ?? '');

$errors = [];

if (empty($firstName)) $errors[] = 'First name is required.';
if (strlen($firstName) > 100) $errors[] = 'First name is too long.';
if (empty($lastName)) $errors[] = 'Last name is required.';
if (strlen($lastName) > 100) $errors[] = 'Last name is too long.';
if (empty($email)) $errors[] = 'Email is required.';
if (!validateEmail($email)) $errors[] = 'Please provide a valid email address.';
if (empty($message)) $errors[] = 'Message is required.';
if (strlen($message) > 5000) $errors[] = 'Message is too long.';

if (!empty($errors)) {
    jsonResponse(['error' => implode(' ', $errors)], 422);
}

$data = [
    'firstName' => $firstName,
    'lastName' => $lastName,
    'email' => $email,
    'interest' => $interest,
    'message' => $message,
];

$saved = saveMessage($data);

EmailSender::sendContactEmail($data);

if ($saved) {
    jsonResponse([
        'success' => true,
        'message' => "Thank you, {$firstName}! Your message has been sent successfully. We will contact you soon. 🇬🇧"
    ]);
} else {
    jsonResponse(['error' => 'Failed to save your message. Please try again.'], 500);
}
