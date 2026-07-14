// Auth: mostra overlay de login se não autenticado; esconde o app.
(async () => {
  const overlay = document.getElementById("login-overlay");
  const logoutBtn = document.getElementById("logout-btn");
  const form = document.getElementById("login-form");

  async function checkAuth() {
    try {
      const r = await fetch("/api/auth/me");
      if (r.ok) {
        overlay.style.display = "none";
        return;
      }
    } catch (_) {}
    overlay.style.display = "flex";
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const user = document.getElementById("login-user").value;
      const password = document.getElementById("login-pass").value;
      const err = document.getElementById("login-error");
      err.textContent = "";
      try {
        const r = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user, password }),
        });
        if (r.ok) location.reload();
        else err.textContent = "Usuário ou senha inválidos";
      } catch (_) {
        err.textContent = "Erro ao conectar";
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      await fetch("/api/auth/logout", { method: "POST" });
      location.reload();
    });
  }

  await checkAuth();
})();
