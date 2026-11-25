(function () {
  "use strict";

  // ---------- Config ----------
  const AGENT_API_BASE = "http://localhost:8000";
  const MANAGEMENT_API_BASE = "http://localhost:8001";

  const QUERY_URL = `${AGENT_API_BASE}/agent/query`;
  const CONVERSATIONS_URL = `${MANAGEMENT_API_BASE}/api/conversations/`;

  const STORAGE_KEY = "kora_nutritional_context";
  const USER_ID_STORAGE_KEY = "kora_user_id";
  const USER_EMAIL_STORAGE_KEY = "kora_user_email";
  const USER_NAME_STORAGE_KEY = "kora_user_name";

  // ---------- DOM ----------
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
  const recentChats = document.getElementById("recentChats");

  if (apiBaseLabel) {
    apiBaseLabel.textContent = AGENT_API_BASE;
  }

  // ---------- State ----------
  let currentSessionId = null;
  let currentConversationId = null;
  let lastPayload = null;
  let lastImage = null;
  let conversation = []; // { role, content, imageDataUrl?, visionResult? }

  // ---------- Helpers ----------
  function parseList(value) {
    if (!value || !value.trim()) return [];
    return value
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
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

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  // ---------- Payload builder ----------
  function buildPayload() {
    loadContextFromStorage();

    const message = messageInput?.value.trim() || "";

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
        allergies,
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

  function showHistoryLoading() {
    if (stateEmpty) stateEmpty.hidden = true;
    if (messagesList) messagesList.hidden = true;
    if (stateLoading) stateLoading.hidden = false;
    if (stateError) stateError.hidden = true;
  }

  function showHistoryError(message) {
    if (stateEmpty) stateEmpty.hidden = true;
    if (messagesList) messagesList.hidden = true;
    if (stateLoading) stateLoading.hidden = true;
    if (stateError) stateError.hidden = false;
    if (errorMessage) errorMessage.textContent = message;
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

  // ---------- Message rendering ----------
  function appendMessage(role, content, options = {}) {
    showChat();

    const { imageDataUrl = null, visionResult = null } = options;

    conversation.push({ role, content, imageDataUrl, visionResult });

    const row = document.createElement("div");
    row.className = `kora-msg kora-msg--${role}`;

    const avatar = document.createElement("div");
    avatar.className = "kora-msg__avatar";
    if (role === "assistant") {
      avatar.innerHTML = '<img src="images/k.svg" alt="Kora" width="28" height="28" />';
    } else {
      avatar.innerHTML = "<span>Tú</span>";
    }

    const bubble = document.createElement("div");
    bubble.className = "kora-msg__bubble";

    if (role === "user" && imageDataUrl) {
      const imgWrap = document.createElement("div");
      imgWrap.className = "kora-msg__image";
      const img = document.createElement("img");
      img.src = imageDataUrl;
      img.alt = "Fotografía enviada";
      img.loading = "lazy";
      imgWrap.appendChild(img);
      bubble.appendChild(imgWrap);
    }

    if (role === "assistant") {
      if (visionResult) {
        bubble.appendChild(renderVisionResult(visionResult));
      }
      if (content) {
        const textDiv = document.createElement("div");
        textDiv.className = "kora-msg__text";
        textDiv.innerHTML = DOMPurify.sanitize(marked.parse(content));
        bubble.appendChild(textDiv);
      }
    } else if (content) {
      const textNode = document.createElement("div");
      textNode.className = "kora-msg__text";
      textNode.textContent = content;
      bubble.appendChild(textNode);
    }

    row.appendChild(avatar);
    row.appendChild(bubble);

    if (messagesList) messagesList.appendChild(row);

    requestAnimationFrame(() => {
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    });
  }

  function renderVisionResult(result) {
    const card = document.createElement("div");
    card.className = "kora-vision-card";

    const status = result.status || "error";
    const success = result.success === true;
    const predictions = Array.isArray(result.predictions) ? result.predictions : [];
    const message = result.message || "";

    let titleText = "Análisis de imagen";
    let statusClass = "kora-vision-card__status--error";

    if (status === "identified" && success && predictions.length) {
      titleText = "Alimentos identificados";
      statusClass = "kora-vision-card__status--ok";
    } else if (status === "uncertain") {
      titleText = "Identificación incierta";
      statusClass = "kora-vision-card__status--warn";
    } else {
      titleText = "No se pudieron reconocer alimentos";
      statusClass = "kora-vision-card__status--error";
    }

    const header = document.createElement("div");
    header.className = "kora-vision-card__header";
    header.innerHTML = `
      <span class="kora-vision-card__title">${titleText}</span>
      <span class="kora-vision-card__status ${statusClass}">${status}</span>
    `;
    card.appendChild(header);

    if (message) {
      const msgEl = document.createElement("p");
      msgEl.className = "kora-vision-card__message";
      msgEl.textContent = message;
      card.appendChild(msgEl);
    }

    if (predictions.length) {
      const list = document.createElement("ul");
      list.className = "kora-vision-card__list";

      predictions.forEach((p) => {
        const li = document.createElement("li");
        const food = p.food || "Desconocido";
        const score = typeof p.score === "number" ? p.score : null;
        const scoreLabel = score !== null ? `puntuación relativa: ${score.toFixed(3)}` : "";

        li.innerHTML = `<strong>${escapeHtml(food)}</strong>${
          scoreLabel ? ` <span class="kora-vision-card__score">(${scoreLabel})</span>` : ""
        }`;
        list.appendChild(li);
      });

      card.appendChild(list);

      const note = document.createElement("p");
      note.className = "kora-vision-card__note";
      note.textContent =
        "Las puntuaciones son valores relativos del modelo (SVM), no porcentajes de certeza calibrada.";
      card.appendChild(note);
    } else if (status !== "identified") {
      const empty = document.createElement("p");
      empty.className = "kora-vision-card__empty";
      empty.textContent =
        "No se detectaron alimentos con suficiente confianza, o el análisis falló. Puedes probar con otra fotografía más clara o en mejor iluminación.";
      card.appendChild(empty);
    }

    return card;
  }

  function clearConversation() {
    conversation = [];
    if (messagesList) messagesList.innerHTML = "";
    showEmpty();
  }

  // ---------- Auth (opcional: solo para historial persistente) ----------
  function getCurrentUserId() {
    return localStorage.getItem(USER_ID_STORAGE_KEY);
  }

  function isUserLoggedIn() {
    return !!getCurrentUserId();
  }

  function updateAuthUI() {
    const btn = document.getElementById("btnOpenLogin");
    if (!btn) return;

    if (isUserLoggedIn()) {
      const name =
        localStorage.getItem(USER_NAME_STORAGE_KEY) ||
        localStorage.getItem(USER_EMAIL_STORAGE_KEY) ||
        "Sesión activa";
      btn.textContent = "Cerrar sesión";
      btn.title = name;
      btn.classList.add("is-logged-in");
    } else {
      btn.textContent = "Iniciar sesión";
      btn.title = "";
      btn.classList.remove("is-logged-in");
    }
  }

  // ---------- Conversation history (management API) ----------
  async function createConversation(firstMessage) {
    const userId = getCurrentUserId();

    if (!userId) {
      throw new Error("No se encontró el identificador del usuario.");
    }

    const title = firstMessage.trim().substring(0, 60) || "Nueva conversación";

    const res = await fetch(CONVERSATIONS_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        user_id: userId,
        title: title,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || data.detail || `Error HTTP ${res.status}`);
    }

    currentConversationId = data.id;

    return data;
  }

  async function sendMessageToManagement(message) {
    const userId = getCurrentUserId();

    if (!userId) {
      throw new Error("No se encontró el identificador del usuario.");
    }

    if (!currentConversationId) {
      await createConversation(message);
    }

    const url = `${CONVERSATIONS_URL}${encodeURIComponent(currentConversationId)}/messages/`;

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        user_id: userId,
        message: message,
      }),
    });

    let data = null;

    try {
      data = await res.json();
    } catch (_) {}

    if (!res.ok) {
      const detail =
        data?.error || data?.detail || `Error HTTP ${res.status}`;

      throw new Error(detail);
    }

    return data;
  }

  function renderConversations(conversations) {
    if (!recentChats) return;

    recentChats.innerHTML = "";

    if (!conversations.length) {
      const emptyMessage = document.createElement("p");
      emptyMessage.className = "kora-sidebar__empty";
      emptyMessage.textContent = "No hay conversaciones disponibles.";
      recentChats.appendChild(emptyMessage);
      return;
    }

    conversations.forEach((item) => {
      const button = document.createElement("button");

      button.type = "button";
      button.className = "kora-recent-item";
      button.textContent = item.title || "Nueva conversación";
      button.dataset.conversationId = item.id;

      if (item.id === currentConversationId) {
        button.classList.add("is-active");
      }

      button.addEventListener("click", async () => {
        currentConversationId = item.id;

        recentChats.querySelectorAll(".kora-recent-item").forEach((el) => {
          el.classList.remove("is-active");
        });

        button.classList.add("is-active");

        const userId = getCurrentUserId();

        if (!userId) return;

        showHistoryLoading();

        try {
          const history = await loadConversationHistory(
            userId,
            currentConversationId
          );

          renderConversationMessages(history.messages || []);
        } catch (err) {
          console.error("Failed to load conversation history:", err);

          showHistoryError(
            "No se pudo cargar el historial. Verifica svc-management."
          );
        }
      });

      recentChats.appendChild(button);
    });
  }

  function renderConversationMessages(messages) {
    conversation = [];

    if (messagesList) {
      messagesList.innerHTML = "";
    }

    if (!messages.length) {
      showEmpty();
      return;
    }

    messages.forEach((msg) => {
      appendMessage(msg.role, msg.content);
    });

    showChat();
  }

  async function loadConversations(userId) {
    if (!userId) return [];

    const url = `${CONVERSATIONS_URL}?user_id=${encodeURIComponent(userId)}`;

    const res = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data.error || data.detail || `Error HTTP ${res.status}`
      );
    }

    return Array.isArray(data) ? data : [];
  }

  async function loadConversationHistory(userId, conversationId) {
    if (!userId || !conversationId) return null;

    const url =
      `${CONVERSATIONS_URL}${encodeURIComponent(conversationId)}/history/` +
      `?user_id=${encodeURIComponent(userId)}`;

    const res = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data.error || data.detail || `Error HTTP ${res.status}`
      );
    }

    return data;
  }

  async function refreshConversations() {
    const userId = getCurrentUserId();

    if (!userId) return;

    const conversations = await loadConversations(userId);
    renderConversations(conversations);
  }

  /**
   * Llamada directa a svc-agent (FormData).
   * Es el mismo camino que ya te funcionaba para texto e imágenes.
   */
  async function queryAgentDirect(payload, imageMeta) {
    const body = new FormData();

    body.append("message", payload.message || "");
    body.append("session_id", payload.session_id || "");

    body.append(
      "nutritional_context",
      payload.nutritional_context
        ? JSON.stringify(payload.nutritional_context)
        : ""
    );

    if (imageMeta?.file) {
      body.append(
        "image",
        imageMeta.file,
        imageMeta.name || imageMeta.file.name || "image.jpg"
      );
    }

    const res = await fetch(QUERY_URL, {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
      body,
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data.detail || data.message || `Error HTTP ${res.status}`
      );
    }

    return data;
  }

  // ---------- Main query ----------
  async function sendQuery(payload, isRetry = false, imageMeta = null) {
    setLoading(true);

    lastPayload = payload;
    lastImage = imageMeta;

    if (!isRetry) {
      appendMessage("user", payload.message, {
        imageDataUrl: imageMeta ? imageMeta.dataUrl : null,
      });

      if (messageInput) {
        messageInput.value = "";
        autoResize();
      }

      if (imageMeta && window.clearSelectedImage) {
        window.clearSelectedImage();
      }
    }

    try {
      // 1) Imágenes: siempre directo a svc-agent (como antes).
      // 2) Texto SIN user_id: directo a svc-agent (como el archivo que te funcionaba).
      // 3) Texto CON user_id: management (guarda historial). Si falla, fallback a agent.
      const hasImage = !!imageMeta?.file;
      const userId = getCurrentUserId();
      const useManagement = !hasImage && !!userId;

      if (useManagement) {
        try {
          const data = await sendMessageToManagement(payload.message);
          const assistantContent = data.assistant_message?.content || "";
          const assistantMessage = data.assistant_message;

          if (assistantMessage) {
            appendMessage("assistant", assistantContent);
          } else {
            throw new Error(
              "svc-management no devolvió la respuesta del agente."
            );
          }

          await refreshConversations();

          lastPayload = null;
          lastImage = null;
          return;
        } catch (mgmtErr) {
          // Fallback: si management falla (p.ej. agent_client con JSON),
          // no bloqueamos el chat: usamos el agent directo.
          console.warn(
            "Management falló; usando svc-agent directo:",
            mgmtErr
          );
        }
      }

      // Ruta directa a agent (imágenes, sin login, o fallback)
      const data = await queryAgentDirect(payload, imageMeta);

      const text = data.response ?? "";

      if (data.session_id) {
        currentSessionId = data.session_id;
        updateSessionUI();
      }

      const visionResult = data.vision_result || null;

      appendMessage("assistant", text, {
        visionResult,
      });

      lastPayload = null;
      lastImage = null;

      if (window.clearSelectedImage) {
        window.clearSelectedImage();
      }
    } catch (err) {
      console.error("Error sending message:", err);

      const msg =
        err.name === "TypeError"
          ? "No se pudo conectar con los servicios de Kora AI. Verifica que estén funcionando."
          : err.message || "Error desconocido.";

      if (errorMessage) {
        errorMessage.textContent = msg;
      }

      if (stateError) {
        stateError.hidden = false;
      }
    } finally {
      setLoading(false);
    }
  }

  // ---------- Event listeners ----------
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (stateError) stateError.hidden = true;

      const payload = buildPayload();
      const selectedImage = window.getSelectedImage
        ? window.getSelectedImage()
        : null;
      const hasImage = !!selectedImage;

      if (!payload.message && !hasImage) {
        if (errorMessage) {
          errorMessage.textContent =
            "Escribe un mensaje o selecciona una fotografía para continuar.";
        }
        if (stateError) stateError.hidden = false;
        return;
      }

      // Ya NO se bloquea el chat sin login: el texto va al agent directo.
      // Login solo habilita historial persistente en management.

      if (!payload.message && hasImage) {
        payload.message =
          "Analiza los alimentos visibles en esta fotografía e identifica qué contiene, con sus niveles de confianza.";
      }

      let imageMeta = null;
      if (hasImage) {
        const imageData = await window.getSelectedImageAsBase64();
        if (!imageData) {
          if (errorMessage) {
            errorMessage.textContent =
              "No se pudo leer la imagen. Intenta seleccionarla nuevamente.";
          }
          if (stateError) stateError.hidden = false;
          return;
        }
        imageMeta = {
          file: selectedImage,
          name: selectedImage.name,
          dataUrl: imageData.dataUrl,
        };
      }

      await sendQuery(payload, false, imageMeta);
    });
  }

  if (btnRetry) {
    btnRetry.addEventListener("click", () => {
      if (lastPayload) {
        sendQuery(lastPayload, true, lastImage);
      } else {
        form?.requestSubmit();
      }
    });
  }

  if (btnClearSession) {
    btnClearSession.addEventListener("click", async () => {
      if (!currentSessionId) return;
      try {
        await fetch(
          `${AGENT_API_BASE}/agent/memory/${encodeURIComponent(currentSessionId)}`,
          { method: "DELETE" }
        );
      } catch (_) {}
      currentSessionId = null;
      updateSessionUI();
      clearConversation();
    });
  }

  if (btnNewChat) {
    btnNewChat.addEventListener("click", () => {
      currentSessionId = null;
      currentConversationId = null;

      updateSessionUI();
      clearConversation();

      if (recentChats) {
        recentChats.querySelectorAll(".kora-recent-item").forEach((el) => {
          el.classList.remove("is-active");
        });
      }

      if (messageInput) {
        messageInput.focus();
      }
    });
  }

  document.querySelectorAll(".kora-suggestion").forEach((btn) => {
    btn.addEventListener("click", () => {
      const prompt = btn.getAttribute("data-prompt");
      if (prompt && messageInput) {
        messageInput.value = prompt;
        autoResize();
        form?.requestSubmit();
      }
    });
  });

  function autoResize() {
    if (!messageInput) return;
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + "px";
  }

  if (messageInput) {
    messageInput.addEventListener("input", autoResize);
    messageInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form?.requestSubmit();
      }
    });
  }

  // Sidebar collapse
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

  // ---------- Init ----------
  loadContextFromStorage();
  updateSessionUI();
  updateAuthUI();
  showEmpty();

  window.addEventListener("kora:user-logged-in", (event) => {
    updateAuthUI();
    currentConversationId = null;
    clearConversation();

    const list = event.detail?.conversations;
    if (Array.isArray(list)) {
      renderConversations(list);
    } else {
      refreshConversations().catch((err) => {
        console.error("Failed to load conversations after login:", err);
      });
    }
  });

  window.addEventListener("kora:user-logged-out", () => {
    updateAuthUI();
    currentConversationId = null;
    currentSessionId = null;
    updateSessionUI();
    clearConversation();
    if (recentChats) {
      recentChats.innerHTML = "";
      const emptyMessage = document.createElement("p");
      emptyMessage.className = "kora-sidebar__empty";
      emptyMessage.textContent =
        "Inicia sesión para ver el historial guardado (opcional).";
      recentChats.appendChild(emptyMessage);
    }
  });

  const currentUserId = getCurrentUserId();

  if (currentUserId) {
    refreshConversations().catch((err) => {
      console.error("Failed to load conversations:", err);

      if (recentChats) {
        recentChats.innerHTML = "";

        const errorItem = document.createElement("p");
        errorItem.className = "kora-sidebar__empty";
        errorItem.textContent =
          "No se pudieron cargar las conversaciones.";

        recentChats.appendChild(errorItem);
      }
    });
  } else if (recentChats) {
    recentChats.innerHTML = "";
    const emptyMessage = document.createElement("p");
    emptyMessage.className = "kora-sidebar__empty";
    emptyMessage.textContent =
      "Inicia sesión para ver el historial guardado (opcional).";
    recentChats.appendChild(emptyMessage);
  }
})();
