// Auth: mostra overlay de login se não autenticado; esconde o app.
(async () => {
  const overlay = document.getElementById("login-overlay");
  const logoutBtn = document.getElementById("logout-btn");
  const form = document.getElementById("login-form");

  async function checkAuth() {
    try {
      const r = await fetch("/api/auth/me");
      if (r.ok) {
        const d = await r.json().catch(() => ({}));
        overlay.style.display = "none";
        if (!d.is_admin) {
          document.getElementById("users-btn")?.style.setProperty("display", "none");
        }
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
        if (r.ok) window.location.href = "/";
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

  // --- Troca de senha (modal) ---
  const cpModal = document.getElementById("change-pass-modal");
  const cpForm = document.getElementById("change-pass-form");
  const cpErr = document.getElementById("change-pass-error");
  const cpOk = document.getElementById("change-pass-ok");
  document.getElementById("change-pass-btn")?.addEventListener("click", () => {
    cpErr.textContent = "";
    cpOk.textContent = "";
    cpForm.reset();
    cpModal.style.display = "flex";
  });
  document.getElementById("cp-cancel")?.addEventListener("click", () => {
    cpModal.style.display = "none";
  });
  if (cpForm) {
    cpForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      cpErr.textContent = "";
      cpOk.textContent = "";
      const current_password = document.getElementById("cp-current").value;
      const new_password = document.getElementById("cp-new").value;
      const confirm = document.getElementById("cp-confirm").value;
      if (new_password !== confirm) {
        cpErr.textContent = "As senhas não conferem";
        return;
      }
      try {
        const r = await fetch("/api/auth/change-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ current_password, new_password }),
        });
        if (r.ok) {
          cpOk.textContent = "Senha alterada com sucesso!";
          setTimeout(() => (cpModal.style.display = "none"), 1200);
        } else {
          const d = await r.json().catch(() => ({}));
          cpErr.textContent = d.detail || "Erro ao trocar senha";
        }
      } catch {
        cpErr.textContent = "Erro ao conectar";
      }
    });
  }

  // --- Gerenciar usuários (modal) ---
  const uModal = document.getElementById("users-modal");
  const uForm = document.getElementById("users-form");
  const uErr = document.getElementById("users-error");
  const uOk = document.getElementById("users-ok");
  const uList = document.getElementById("users-list");

  async function refreshUsers() {
    try {
      const r = await fetch("/api/auth/users");
      if (r.ok) {
        const d = await r.json();
        uList.innerHTML = "";
        (d.users || []).forEach((u) => {
          const li = document.createElement("li");
          li.textContent = u;
          uList.appendChild(li);
        });
      }
    } catch (_) {}
  }

  document.getElementById("users-btn")?.addEventListener("click", () => {
    uErr.textContent = "";
    uOk.textContent = "";
    uForm.reset();
    uModal.style.display = "flex";
    refreshUsers();
  });
  document.getElementById("users-cancel")?.addEventListener("click", () => {
    uModal.style.display = "none";
  });
  if (uForm) {
    uForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      uErr.textContent = "";
      uOk.textContent = "";
      const username = document.getElementById("u-username").value.trim();
      const password = document.getElementById("u-password").value;
      const confirm = document.getElementById("u-confirm").value;
      if (password !== confirm) {
        uErr.textContent = "As senhas não conferem";
        return;
      }
      try {
        const r = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });
        if (r.ok) {
          uOk.textContent = "Usuário criado!";
          uForm.reset();
          refreshUsers();
        } else {
          const d = await r.json().catch(() => ({}));
          uErr.textContent = d.detail || "Erro ao criar usuário";
        }
      } catch {
        uErr.textContent = "Erro ao conectar";
      }
    });
  }

  await checkAuth();
})();
