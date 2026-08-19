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
if (isRateLimited('waitlist_' . $ip)) {
    jsonResponse(['error' => 'Too many requests. Please try again later.'], 429);
}

$email = trim($_POST['email'] ?? '');

if (empty($email)) {
    jsonResponse(['error' => 'Email is required.'], 422);
}
if (!validateEmail($email)) {
    jsonResponse(['error' => 'Please provide a valid email address.'], 422);
}

$added = saveWaitlist($email);

if ($added) {
    EmailSender::sendWaitlistConfirmation($email);
    jsonResponse([
        'success' => true,
        'message' => "Thank you! {$email} has been added to the Britlearn App waitlist. 🚀"
    ]);
} else {
    jsonResponse([
        'error' => 'This email is already on the waitlist.'
    ], 409);
}
