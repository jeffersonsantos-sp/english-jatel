<?php
require_once __DIR__ . '/../includes/functions.php';

header('Content-Type: application/json; charset=utf-8');

$action = $_GET['action'] ?? $_POST['action'] ?? '';

switch ($action) {
    case 'login':
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            jsonResponse(['error' => 'Method not allowed'], 405);
        }

        if (!verifyCsrfToken()) {
            jsonResponse(['error' => 'Invalid security token.'], 403);
        }

        $username = trim($_POST['username'] ?? '');
        $password = $_POST['password'] ?? '';

        if ($username === ADMIN_USER && password_verify($password, ADMIN_PASS_HASH)) {
            session_regenerate_id(true);
            $_SESSION['admin_logged_in'] = true;
            $_SESSION['admin_user'] = $username;
            $_SESSION['login_time'] = time();
            jsonResponse(['success' => true, 'redirect' => '/admin/']);
        } else {
            jsonResponse(['error' => 'Invalid credentials.'], 401);
        }
        break;

    case 'logout':
        session_destroy();
        jsonResponse(['success' => true, 'redirect' => '/admin/login.php']);
        break;

    default:
        jsonResponse(['error' => 'Invalid action'], 400);
        break;
}
