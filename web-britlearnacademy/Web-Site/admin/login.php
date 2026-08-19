<?php
require_once __DIR__ . '/../includes/functions.php';
if (isLoggedIn()) {
    header('Location: /admin/');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Login | <?= SITE_NAME ?></title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans',sans-serif;background:#f8f7f4;display:flex;justify-content:center;align-items:center;min-height:100vh;color:#243447}
.login-box{background:#fff;border-radius:20px;padding:48px;max-width:420px;width:100%;box-shadow:0 20px 60px rgba(13,27,42,.12)}
.login-box h1{font-size:1.5rem;margin-bottom:8px}
.login-box p{color:#6b7280;margin-bottom:32px}
.form-group{margin-bottom:20px}
.form-group label{display:block;font-weight:600;margin-bottom:6px;font-size:14px}
.form-group input{width:100%;padding:14px 16px;border:2px solid #e5e7eb;border-radius:12px;font-size:15px;font-family:inherit;transition:border-color .2s}
.form-group input:focus{outline:none;border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,.15)}
.btn{width:100%;padding:14px;background:#0d1b2a;color:#fff;border:none;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;font-family:inherit;transition:transform .2s}
.btn:hover{transform:translateY(-2px)}
.error{color:#dc2626;font-size:14px;margin-top:12px;display:none}
.logo-link{display:flex;align-items:center;gap:8px;text-decoration:none;color:#0d1b2a;font-size:1.1rem;font-weight:700;margin-bottom:32px}
.logo-link span:first-child{font-size:1.5rem}
</style>
</head>
<body>
<div class="login-box">
<a href="/britlearnacademy/" class="logo-link"><span>🇬🇧</span> <?= SITE_NAME ?></a>
<h1>Admin Login</h1>
<p>Enter your credentials to access the dashboard.</p>
<form id="loginForm">
<?= csrfField() ?>
<div class="form-group">
<label for="username">Username</label>
<input type="text" id="username" name="username" required autocomplete="username">
</div>
<div class="form-group">
<label for="password">Password</label>
<input type="password" id="password" name="password" required autocomplete="current-password">
</div>
<button type="submit" class="btn">Sign In</button>
<p class="error" id="loginError"></p>
</form>
</div>
<script>
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById('loginError');
    errorEl.style.display = 'none';
    const formData = new FormData(e.target);
    try {
        const res = await fetch('/britlearnacademy/api/auth.php?action=login', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            errorEl.textContent = data.error || 'Login failed.';
            errorEl.style.display = 'block';
        }
    } catch (err) {
        errorEl.textContent = 'Connection error. Please try again.';
        errorEl.style.display = 'block';
    }
});
</script>
</body>
</html>
