<?php
require_once __DIR__ . '/../includes/functions.php';
requireLogin();

if (isset($_GET['read'])) {
    $id = (int) $_GET['read'];
    markAsRead($id);
    header('Location: /admin/');
    exit;
}

header('Location: /admin/');
exit;
