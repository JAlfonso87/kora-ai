(function () {
  "use strict";

  const USER_ID_STORAGE_KEY = "kora_user_id";
  const USER_EMAIL_STORAGE_KEY = "kora_user_email";
  const USER_NAME_STORAGE_KEY = "kora_user_name";

  // Usuario de prueba documentado en svc-management/scripts/create_test_data.py
  const DEMO_EMAIL = "prueba.kora@example.com";
  const DEMO_PASSWORD = "KoraPrueba2026!";

  const modal = document.getElementById("loginModal");
  const openBtn = document.getElementById("btnOpenLogin");
  const loginForm = document.getElementById("loginForm");
  const loginEmail = document.getElementById("loginEmail");
  const loginPassword = document.getElementById("loginPassword");
  const loginUserId = document.getElementById("loginUserId");
  const loginError = document.getElementById("loginError");
  const loginSubmitBtn = document.getElementById("loginSubmitBtn");

  if (!modal || !openBtn) return;

  function openLogin() {
    modal.hidden = false;
    modal.setAttribute("aria-hidden", "false");
    if (loginError) {
      loginError.hidden = true;
      loginError.textContent = "";
    }
    const savedEmail = localStorage.getItem(USER_EMAIL_STORAGE_KEY);
    if (loginEmail && savedEmail) loginEmail.value = savedEmail;
    const savedUserId = localStorage.getItem(USER_ID_STORAGE_KEY);
    if (loginUserId && savedUserId) loginUserId.value = savedUserId;
    loginEmail?.focus();
  }

  function closeLogin() {
    modal.hidden = true;
    modal.setAttribute("aria-hidden", "true");
  }

  function showLoginError(message) {
    if (!loginError) return;
    loginError.textContent = message;
    loginError.hidden = false;
  }

  function isValidUuid(value) {
    if (!value || typeof value !== "string") return false;
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      value.trim()
    );
  }

  function persistSession(userId, email, name) {
    localStorage.setItem(USER_ID_STORAGE_KEY, userId.trim());
    if (email) localStorage.setItem(USER_EMAIL_STORAGE_KEY, email.trim());
    if (name) localStorage.setItem(USER_NAME_STORAGE_KEY, name);
    else localStorage.removeItem(USER_NAME_STORAGE_KEY);
  }

  function clearSession() {
    localStorage.removeItem(USER_ID_STORAGE_KEY);
    localStorage.removeItem(USER_EMAIL_STORAGE_KEY);
    localStorage.removeItem(USER_NAME_STORAGE_KEY);
  }

  async function handleLogin(e) {
    e.preventDefault();
    if (loginError) {
      loginError.hidden = true;
      loginError.textContent = "";
    }

    const email = (loginEmail?.value || "").trim();
    const password = loginPassword?.value || "";
    const userIdRaw = (loginUserId?.value || "").trim();

    if (!email) {
      showLoginError("Introduce tu email.");
      loginEmail?.focus();
      return;
    }

    if (!password) {
      showLoginError("Introduce tu contraseña.");
      loginPassword?.focus();
      return;
    }

    // Sin endpoint de auth en el backend: se requiere el UUID del usuario
    // creado con scripts/create_test_data.py en svc-management.
    if (!userIdRaw) {
      showLoginError(
        "Indica el User ID (UUID) del usuario en la base de datos. " +
          "Ejecuta create_test_data.py en svc-management y copia el ID impreso."
      );
      loginUserId?.focus();
      return;
    }

    if (!isValidUuid(userIdRaw)) {
      showLoginError("El User ID no es un UUID válido.");
      loginUserId?.focus();
      return;
    }

    if (email.toLowerCase() === DEMO_EMAIL.toLowerCase()) {
      if (password !== DEMO_PASSWORD) {
        showLoginError("Contraseña incorrecta para el usuario de prueba.");
        loginPassword?.focus();
        return;
      }
    }

    if (loginSubmitBtn) {
      loginSubmitBtn.disabled = true;
      loginSubmitBtn.textContent = "Ingresando…";
    }

    try {
      const MANAGEMENT_API_BASE = "http://localhost:8001";
      const url =
        `${MANAGEMENT_API_BASE}/api/conversations/?user_id=` +
        encodeURIComponent(userIdRaw);

      const res = await fetch(url, {
        method: "GET",
        headers: { Accept: "application/json" },
      });

      let data = null;
      try {
        data = await res.json();
      } catch (_) {}

      if (!res.ok) {
        const detail =
          data?.error ||
          data?.detail ||
          `No se pudo validar el usuario (HTTP ${res.status}). ¿Está svc-management en marcha?`;
        throw new Error(
          typeof detail === "string" ? detail : JSON.stringify(detail)
        );
      }

      const displayName =
        email.toLowerCase() === DEMO_EMAIL.toLowerCase()
          ? "Usuario Prueba Kora"
          : email.split("@")[0];

      persistSession(userIdRaw, email, displayName);
      closeLogin();

      window.dispatchEvent(
        new CustomEvent("kora:user-logged-in", {
          detail: {
            userId: userIdRaw,
            email,
            name: displayName,
            conversations: Array.isArray(data) ? data : [],
          },
        })
      );
    } catch (err) {
      console.error("Login failed:", err);
      showLoginError(
        err.message ||
          "No se pudo iniciar sesión. Verifica el User ID y que svc-management esté activo."
      );
    } finally {
      if (loginSubmitBtn) {
        loginSubmitBtn.disabled = false;
        loginSubmitBtn.textContent = "Ingresar";
      }
    }
  }

  function handleLogout() {
    clearSession();
    window.dispatchEvent(new CustomEvent("kora:user-logged-out"));
  }

  window.koraAuth = {
    openLogin,
    closeLogin,
    logout: handleLogout,
    getUserId: () => localStorage.getItem(USER_ID_STORAGE_KEY),
    getEmail: () => localStorage.getItem(USER_EMAIL_STORAGE_KEY),
    getName: () => localStorage.getItem(USER_NAME_STORAGE_KEY),
    isLoggedIn: () => !!localStorage.getItem(USER_ID_STORAGE_KEY),
  };

  openBtn.addEventListener("click", () => {
    if (window.koraAuth.isLoggedIn()) {
      handleLogout();
    } else {
      openLogin();
    }
  });

  modal.querySelectorAll("[data-close-login]").forEach((el) => {
    el.addEventListener("click", closeLogin);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.hidden) closeLogin();
  });

  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
  }

  if (loginSubmitBtn && loginSubmitBtn.type === "button") {
    loginSubmitBtn.addEventListener("click", (e) => {
      e.preventDefault();
      loginForm?.requestSubmit();
    });
  }
})();
