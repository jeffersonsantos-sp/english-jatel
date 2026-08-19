<?php
require_once __DIR__ . '/includes/functions.php';

$page = $_GET['page'] ?? 'home';

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
