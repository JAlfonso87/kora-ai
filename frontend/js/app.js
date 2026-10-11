
(function () {
  "use strict";

  const API_BASE = "http://localhost:8000";
  const QUERY_URL = `${API_BASE}/agent/query`;
  const STORAGE_KEY = "kora_nutritional_context";

  const form = document.getElementById("queryForm");
  const btnSubmit = document.getElementById("btnSubmit");
  const btnClearSession = document.getElementById("btnClearSession");
  const btnRetry = document.getElementById("btnRetry");
  const btnNewChat = document.getElementById("btnNewChat");
  const sessionBadge = document.getElementById("sessionBadge");
  const apiBaseLabel = document.getElementById("apiBaseLabel");
  const messageInput = document.getElementById("message");

  const stateEmpty = document.getElementById("stateEmpty");
  const stateLoading = document.getElementById("stateLoading");
  const stateError = document.getElementById("stateError");
  const messagesList = document.getElementById("messagesList");
  const errorMessage = document.getElementById("errorMessage");
  const chatContainer = document.getElementById("chatContainer");

  if (apiBaseLabel) apiBaseLabel.textContent = API_BASE;

  let currentSessionId = null;
  let lastPayload = null;
  let conversation = []; // { role: 'user'|'assistant', content: string }

  // ---------- helpers ----------
  function parseList(value) {
    if (!value || !value.trim()) return [];
    return value.split(",").map((s) => s.trim()).filter(Boolean);
  }

  function numOrNull(value) {
    if (value === "" || value === null || value === undefined) return null;
    const n = Number(value);
    return Number.isFinite(n) && n > 0 ? n : null;
  }

  function numOrZero(value) {
    if (value === "" || value === null || value === undefined) return null;
    const n = Number(value);
    return Number.isFinite(n) && n >= 0 ? n : null;
  }

  function loadContextFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const data = JSON.parse(raw);
      Object.keys(data).forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = data[id] ?? "";
      });
    } catch (_) {}
  }

  function buildPayload() {
    loadContextFromStorage();

    const message = messageInput.value.trim();

    const primary = document.getElementById("goalPrimary")?.value || null;
    const calorieTarget = numOrNull(document.getElementById("calorieTarget")?.value);
    const proteinTarget = numOrNull(document.getElementById("proteinTarget")?.value);
    let goals = null;
    if (primary && calorieTarget !== null && proteinTarget !== null) {
      goals = {
        primary,
        calorie_target_kcal: calorieTarget,
        protein_target_g: proteinTarget,
      };
    }

    const caloriesConsumed = numOrZero(document.getElementById("caloriesConsumed")?.value);
    const proteinConsumed = numOrZero(document.getElementById("proteinConsumed")?.value);
    let current_consumption = null;
    if (caloriesConsumed !== null && proteinConsumed !== null) {
      current_consumption = {
        calories_kcal: caloriesConsumed,
        protein_g: proteinConsumed,
      };
    }

    const caloriesRemaining = numOrZero(document.getElementById("caloriesRemaining")?.value);
    const proteinRemaining = numOrZero(document.getElementById("proteinRemaining")?.value);
    let remaining_nutrients = null;
    if (caloriesRemaining !== null && proteinRemaining !== null) {
      remaining_nutrients = {
        calories_kcal: caloriesRemaining,
        protein_g: proteinRemaining,
      };
    }

    const preferred = parseList(document.getElementById("preferredFoods")?.value || "");
    let preferences = null;
    if (preferred.length) {
      preferences = { preferred_foods: preferred };
    }

    const avoided = parseList(document.getElementById("avoidedFoods")?.value || "");
    const unavailable = parseList(document.getElementById("unavailableFoods")?.value || "");
    const allergies = parseList(document.getElementById("allergies")?.value || "");
    let restrictions = null;
    if (avoided.length || unavailable.length || allergies.length) {
      restrictions = {
        avoided_foods: avoided,
        unavailable_foods: unavailable,
        allergies: allergies,
      };
    }

    const age = numOrNull(document.getElementById("age")?.value);
    const sex = document.getElementById("sex")?.value || null;
    const weightKg = numOrNull(document.getElementById("weightKg")?.value);
    const heightCm = numOrNull(document.getElementById("heightCm")?.value);
    let user_profile = null;
    if (age !== null && sex && weightKg !== null && heightCm !== null) {
      user_profile = {
        age,
        sex,
        weight_kg: weightKg,
        height_cm: heightCm,
      };
    }

    const contextParts = {
      user_profile,
      goals,
      current_consumption,
      remaining_nutrients,
      preferences,
      restrictions,
    };
    const hasContext = Object.values(contextParts).some((v) => v !== null);
    const nutritional_context = hasContext ? contextParts : null;

    return {
      message,
      session_id: currentSessionId || null,
      nutritional_context,
    };
    
  }

  // ---------- UI states ----------
  function showEmpty() {
    if (stateEmpty) stateEmpty.hidden = false;
    if (messagesList) messagesList.hidden = true;
    if (stateLoading) stateLoading.hidden = true;
    if (stateError) stateError.hidden = true;
  }

  function showChat() {
    if (stateEmpty) stateEmpty.hidden = true;
    if (messagesList) messagesList.hidden = false;
    if (stateLoading) stateLoading.hidden = true;
    if (stateError) stateError.hidden = true;
  }

  function setLoading(isLoading) {
    if (btnSubmit) {
      btnSubmit.disabled = isLoading;
      btnSubmit.classList.toggle("is-loading", isLoading);
    }
    if (stateLoading) stateLoading.hidden = !isLoading;
    if (isLoading && stateError) stateError.hidden = true;
  }

  function updateSessionUI() {
    if (!sessionBadge) return;
    if (currentSessionId) {
      const short = currentSessionId.slice(0, 8) + "…";
      sessionBadge.textContent = short;
      sessionBadge.title = currentSessionId;
      if (btnClearSession) btnClearSession.disabled = false;
    } else {
      sessionBadge.textContent = "Sin sesión";
      sessionBadge.title = "";
      if (btnClearSession) btnClearSession.disabled = true;
    }
  }

  // ---------- messages ----------
  function appendMessage(role, content) {
    showChat();
    conversation.push({ role, content });

    const row = document.createElement("div");
    row.className = `kora-msg kora-msg--${role}`;

    const avatar = document.createElement("div");
    avatar.className = "kora-msg__avatar";
    if (role === "assistant") {
      avatar.innerHTML = `<img src="images/k.svg" alt="Kora" width="28" height="28" />`;
    } else {
      avatar.innerHTML = `<span>Tú</span>`;
    }

    const bubble = document.createElement("div");
    bubble.className = "kora-msg__bubble";

    if (role === "assistant") {
      bubble.innerHTML = DOMPurify.sanitize(marked.parse(content));
    } else {
      bubble.textContent = content;
    }

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesList.appendChild(row);

    // scroll to bottom
    requestAnimationFrame(() => {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    });
  }

  function clearConversation() {
    conversation = [];
    if (messagesList) messagesList.innerHTML = "";
    showEmpty();
  }

  // ---------- API ----------
  async function sendQuery(payload) {
    setLoading(true);
    lastPayload = payload;

    // show user message immediately
    appendMessage("user", payload.message);
    messageInput.value = "";
    autoResize();

    try {
      const res = await fetch(QUERY_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(payload),
      });

      let data = null;
      try {
        data = await res.json();
      } catch {
        /* empty */
      }

      if (!res.ok) {
        const detail =
          (data && (data.detail || data.message)) ||
          `Error HTTP ${res.status}`;
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }

      const text = data.response ?? "";
      if (data.session_id) {
        currentSessionId = data.session_id;
        updateSessionUI();
      }

      appendMessage("assistant", text);
    } catch (err) {
      const msg =
        err.name === "TypeError"
          ? `No se pudo conectar con svc-agente (${API_BASE}). ¿Está en ejecución?`
          : err.message || "Error desconocido";
      if (errorMessage) errorMessage.textContent = msg;
      if (stateError) stateError.hidden = false;
      // keep the user message visible
      showChat();
    } finally {
      setLoading(false);
    }
  }

  // ---------- events ----------
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const payload = buildPayload();

      if (!payload.message) {
        if (errorMessage) errorMessage.textContent = "El mensaje no puede estar vacío.";
        if (stateError) stateError.hidden = false;
        messageInput.focus();
        return;
      }

      sendQuery(payload);
    });
  }

  if (btnRetry) {
    btnRetry.addEventListener("click", () => {
      if (lastPayload) {
        // remove last user message if we are retrying (optional: keep history)
        sendQuery(lastPayload);
      } else {
        form?.requestSubmit();
      }
    });
  }

  if (btnClearSession) {
    btnClearSession.addEventListener("click", async () => {
      if (!currentSessionId) return;

      try {
        await fetch(`${API_BASE}/agent/memory/${encodeURIComponent(currentSessionId)}`, {
          method: "DELETE",
        });
      } catch {
        /* ignore */
      }

      currentSessionId = null;
      updateSessionUI();
      clearConversation();
    });
  }

  if (btnNewChat) {
    btnNewChat.addEventListener("click", () => {
      currentSessionId = null;
      updateSessionUI();
      clearConversation();
      messageInput.focus();
    });
  }

  // suggestion chips
  document.querySelectorAll(".kora-suggestion").forEach((btn) => {
    btn.addEventListener("click", () => {
      const prompt = btn.getAttribute("data-prompt");
      if (prompt) {
        messageInput.value = prompt;
        autoResize();
        form?.requestSubmit();
      }
    });
  });

  // auto-resize textarea
  function autoResize() {
    if (!messageInput) return;
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + "px";
  }

  if (messageInput) {
    messageInput.addEventListener("input", autoResize);
    // Enter to send, Shift+Enter for newline
    messageInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form?.requestSubmit();
      }
    });
  }

// sidebar collapse
const btnCollapse = document.getElementById("btnCollapseSidebar");
const btnOpenSidebar = document.getElementById("btnOpenSidebar");
const sidebar = document.getElementById("sidebar");

if (btnCollapse && sidebar) {
  btnCollapse.addEventListener("click", () => {
    document.body.classList.add("sidebar-collapsed");
  });
}

if (btnOpenSidebar && sidebar) {
  btnOpenSidebar.addEventListener("click", () => {
    document.body.classList.remove("sidebar-collapsed");
  });
}

  // init
  loadContextFromStorage();
  updateSessionUI();
  showEmpty();
})();
