<?php
if (!isset($pageTitle)) $pageTitle = SITE_NAME;
if (!isset($pageDescription)) $pageDescription = 'Britlearn Academy is a London-inspired English school helping students communicate confidently since 2001.';
if (!isset($activePage)) $activePage = 'home';
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?= sanitize($pageTitle) ?> | <?= SITE_NAME ?></title>
<meta name="description" content="<?= sanitize($pageDescription) ?>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="<?= ASSETS_URL ?>/css/style.css">
<meta name="csrf-token" content="<?= generateCsrfToken() ?>">
</head>
<body>
<header class="navbar">
<div class="container nav-container">
<a href="index.php" class="logo"><span>🇬🇧</span><span>Britlearn</span><small>ACADEMY</small></a>
<nav class="nav-links" id="navLinks">
<a href="index.php" class="<?= $activePage === 'home' ? 'active' : '' ?>">Home</a>
<a href="index.php#courses" class="<?= $activePage === 'courses' ? 'active' : '' ?>">Courses</a>
<a href="index.php?page=story" class="<?= $activePage === 'story' ? 'active' : '' ?>">Our Story</a>
<a href="index.php?page=contact" class="<?= $activePage === 'contact' ? 'active' : '' ?>">Contact</a>
</nav>
<a href="/app" class="nav-button" target="_blank">BritLearn-APP</a>
<button class="menu-toggle" id="menuToggle">☰</button>
</div>
</header>
