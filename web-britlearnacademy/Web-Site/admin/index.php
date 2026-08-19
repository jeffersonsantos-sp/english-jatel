<?php
require_once __DIR__ . '/../includes/functions.php';
requireLogin();

$messages = getMessages();
$unread = getUnreadCount();
$waitlist = [];
$waitlistFile = DATA_PATH . '/waitlist.json';
if (file_exists($waitlistFile)) {
    $waitlist = json_decode(file_get_contents($waitlistFile), true) ?: [];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Dashboard | <?= SITE_NAME ?></title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans',sans-serif;background:#f8f7f4;color:#243447}
.admin-header{background:#0d1b2a;color:#fff;padding:16px 32px;display:flex;justify-content:space-between;align-items:center}
.admin-header h1{font-size:1.2rem}
.admin-header a{color:#fff;text-decoration:none;padding:8px 16px;border:1px solid rgba(255,255,255,.3);border-radius:8px;font-size:14px}
.admin-header a:hover{background:rgba(255,255,255,.1)}
.container{max-width:1100px;margin:0 auto;padding:32px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:32px}
.stat-card{background:#fff;border-radius:16px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.stat-card .number{font-size:2rem;font-weight:700;color:#2563eb}
.stat-card .label{color:#6b7280;font-size:14px;margin-top:4px}
.section-title{font-size:1.3rem;margin-bottom:16px}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06)}
th,td{padding:14px 20px;text-align:left;border-bottom:1px solid #e5e7eb;font-size:14px}
th{background:#f9fafb;font-weight:600;color:#6b7280;text-transform:uppercase;font-size:12px;letter-spacing:.5px}
tr:hover{background:#f9fafb}
.unread{background:#dbeafe;font-weight:600}
.badge{background:#2563eb;color:#fff;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600}
.empty{text-align:center;padding:40px;color:#6b7280}
.btn-sm{padding:6px 12px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px;text-decoration:none;display:inline-block}
.btn-sm:hover{background:#1d4ed8}
</style>
</head>
<body>
<div class="admin-header">
<h1>🇬🇧 <?= SITE_NAME ?> — Admin</h1>
<div>
<a href="/britlearnacademy/">View Site</a>
<a href="/britlearnacademy/admin/logout.php" style="margin-left:8px">Logout</a>
</div>
</div>
<div class="container">
<div class="stats">
<div class="stat-card"><div class="number"><?= count($messages) ?></div><div class="label">Total Messages</div></div>
<div class="stat-card"><div class="number"><?= $unread ?></div><div class="label">Unread Messages</div></div>
<div class="stat-card"><div class="number"><?= count($waitlist) ?></div><div class="label">Waitlist Signups</div></div>
</div>

<h2 class="section-title">Contact Messages</h2>
<?php if (empty($messages)): ?>
<div class="empty">No messages yet.</div>
<?php else: ?>
<table>
<thead><tr><th>#</th><th>Name</th><th>Email</th><th>Interest</th><th>Date</th><th>Status</th></tr></thead>
<tbody>
<?php foreach ($messages as $msg): ?>
<tr class="<?= !$msg['read'] ? 'unread' : '' ?>">
<td><?= $msg['id'] ?></td>
<td><?= sanitize($msg['firstName'] . ' ' . $msg['lastName']) ?></td>
<td><a href="mailto:<?= sanitize($msg['email']) ?>"><?= sanitize($msg['email']) ?></a></td>
<td><?= sanitize($msg['interest'] ?? '-') ?></td>
<td><?= $msg['created_at'] ?></td>
<td>
<?php if (!$msg['read']): ?>
<a href="/britlearnacademy/admin/messages.php?read=<?= $msg['id'] ?>" class="btn-sm">Mark Read</a>
<?php else: ?>
<span class="badge">Read</span>
<?php endif; ?>
</td>
</tr>
<?php endforeach; ?>
</tbody>
</table>
<?php endif; ?>

<h2 class="section-title" style="margin-top:40px">Waitlist Signups</h2>
<?php if (empty($waitlist)): ?>
<div class="empty">No waitlist signups yet.</div>
<?php else: ?>
<table>
<thead><tr><th>#</th><th>Email</th><th>Date</th></tr></thead>
<tbody>
<?php foreach ($waitlist as $i => $entry): ?>
<tr>
<td><?= $i + 1 ?></td>
<td><a href="mailto:<?= sanitize($entry['email']) ?>"><?= sanitize($entry['email']) ?></a></td>
<td><?= $entry['created_at'] ?></td>
</tr>
<?php endforeach; ?>
</tbody>
</table>
<?php endif; ?>
</div>
</body>
</html>
