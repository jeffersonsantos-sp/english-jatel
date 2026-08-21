<?php
require_once __DIR__ . '/includes/functions.php';

// Handle clean URLs
$requestUri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$requestUri = trim($requestUri, '/');

// Map clean URLs to pages
$pageMap = [
    '' => 'home',
    'story' => 'story',
    'contact' => 'contact',
];

// Check if it's a clean URL
if (isset($pageMap[$requestUri])) {
    $page = $pageMap[$requestUri];
} else {
    // Fallback to query parameter
    $page = $_GET['page'] ?? 'home';
}

$validPages = ['home', 'story', 'contact'];
if (!in_array($page, $validPages)) {
    $page = 'home';
}

switch ($page) {
    case 'story':
        $pageTitle = 'Our Story';
        $pageDescription = 'Since 2001, Britlearn Academy has helped thousands of learners turn English into opportunity.';
        $activePage = 'story';
        break;
    case 'contact':
        $pageTitle = 'Contact';
        $pageDescription = 'Tell us about your goals and we will help you find the right learning path.';
        $activePage = 'contact';
        break;
    default:
        $pageTitle = SITE_NAME;
        $pageDescription = 'Britlearn Academy is a London-inspired English school helping students communicate confidently since 2001.';
        $activePage = 'home';
        break;
}

require_once __DIR__ . '/includes/header.php';
require_once __DIR__ . '/pages/' . $page . '.php';
require_once __DIR__ . '/includes/footer.php';
