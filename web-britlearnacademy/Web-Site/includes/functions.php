<?php
require_once __DIR__ . '/../config/config.php';
require_once __DIR__ . '/email.php';

function generateCsrfToken(): string {
    if (empty($_SESSION[CSRF_TOKEN_NAME])) {
        $_SESSION[CSRF_TOKEN_NAME] = bin2hex(random_bytes(32));
    }
    return $_SESSION[CSRF_TOKEN_NAME];
}

function csrfField(): string {
    return '<input type="hidden" name="' . CSRF_TOKEN_NAME . '" value="' . htmlspecialchars(generateCsrfToken()) . '">';
}

function verifyCsrfToken(): bool {
    $token = $_POST[CSRF_TOKEN_NAME] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    return !empty($token) && hash_equals($_SESSION[CSRF_TOKEN_NAME] ?? '', $token);
}

function sanitize(string $input): string {
    return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
}

function validateEmail(string $email): bool {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

function isRateLimited(string $key): bool {
    $file = DATA_PATH . '/rate_' . md5($key) . '.json';
    $now = time();
    $data = [];
    if (file_exists($file)) {
        $data = json_decode(file_get_contents($file), true) ?: [];
    }
    $data = array_filter($data, fn($t) => $t > $now - RATE_LIMIT_WINDOW);
    if (count($data) >= RATE_LIMIT_MAX) {
        return true;
    }
    $data[] = $now;
    file_put_contents($file, json_encode(array_values($data)));
    return false;
}

function jsonResponse(array $data, int $code = 200): void {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data);
    exit;
}

function saveMessage(array $message): bool {
    $file = DATA_PATH . '/messages.json';
    $messages = [];
    if (file_exists($file)) {
        $messages = json_decode(file_get_contents($file), true) ?: [];
    }
    $message['id'] = count($messages) + 1;
    $message['created_at'] = date('Y-m-d H:i:s');
    $message['read'] = false;
    $messages[] = $message;
    return file_put_contents($file, json_encode($messages, JSON_PRETTY_PRINT)) !== false;
}

function getMessages(): array {
    $file = DATA_PATH . '/messages.json';
    if (!file_exists($file)) return [];
    return array_reverse(json_decode(file_get_contents($file), true) ?: []);
}

function getUnreadCount(): int {
    $messages = getMessages();
    return count(array_filter($messages, fn($m) => !$m['read']));
}

function markAsRead(int $id): bool {
    $file = DATA_PATH . '/messages.json';
    if (!file_exists($file)) return false;
    $messages = json_decode(file_get_contents($file), true) ?: [];
    foreach ($messages as &$msg) {
        if ($msg['id'] === $id) {
            $msg['read'] = true;
            break;
        }
    }
    return file_put_contents($file, json_encode($messages, JSON_PRETTY_PRINT)) !== false;
}

function saveWaitlist(string $email): bool {
    $file = DATA_PATH . '/waitlist.json';
    $list = [];
    if (file_exists($file)) {
        $list = json_decode(file_get_contents($file), true) ?: [];
    }
    foreach ($list as $entry) {
        if ($entry['email'] === $email) return false;
    }
    $list[] = ['email' => $email, 'created_at' => date('Y-m-d H:i:s')];
    return file_put_contents($file, json_encode($list, JSON_PRETTY_PRINT)) !== false;
}

function isLoggedIn(): bool {
    return !empty($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;
}

function requireLogin(): void {
    if (!isLoggedIn()) {
        header('Location: /admin/login.php');
        exit;
    }
}

function setActivePage(string $page): string {
    return isset($_GET['page']) && $_GET['page'] === $page ? 'active' : '';
}
