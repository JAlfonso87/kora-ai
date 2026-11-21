
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

    if (apiBaseLabel) {
        apiBaseLabel.textContent = API_BASE;
    }

    let currentSessionId = null;
    let lastPayload = null;
    let lastImage = null;
    let conversation = [];
  "use strict";

  const AGENT_API_BASE = "http://localhost:8000";
  const MANAGEMENT_API_BASE = "http://localhost:8001";

  const USER_ID_STORAGE_KEY = "kora_user_id";

  const QUERY_URL = `${AGENT_API_BASE}/agent/query`;
  const STORAGE_KEY = "kora_nutritional_context";

  const CONVERSATIONS_URL = `${MANAGEMENT_API_BASE}/api/conversations/`;

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

  if (apiBaseLabel) apiBaseLabel.textContent = AGENT_API_BASE;

  let currentSessionId = null;
  let currentConversationId = null;
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

    function parseList(value) {
        if (!value || !value.trim()) return [];

        return value
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean);
    }

    function numOrNull(value) {
        if (value === "" || value === null || value === undefined) {
            return null;
        }

        const n = Number(value);
        return Number.isFinite(n) && n > 0 ? n : null;
    }

    function numOrZero(value) {
        if (value === "" || value === null || value === undefined) {
            return null;
        }

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

                if (el) {
                    el.value = data[id] ?? "";
                }
            });
        } catch (_) {}
    }

    function buildPayload() {
        loadContextFromStorage();

        const message = messageInput.value.trim();

        const primary =
            document.getElementById("goalPrimary")?.value || null;

        const calorieTarget = numOrNull(
            document.getElementById("calorieTarget")?.value
        );

        const proteinTarget = numOrNull(
            document.getElementById("proteinTarget")?.value
        );

        let goals = null;

        if (primary && calorieTarget !== null && proteinTarget !== null) {
            goals = {
                primary,
                calorie_target_kcal: calorieTarget,
                protein_target_g: proteinTarget
            };
        }

        const caloriesConsumed = numOrZero(
            document.getElementById("caloriesConsumed")?.value
        );

        const proteinConsumed = numOrZero(
            document.getElementById("proteinConsumed")?.value
        );

        let current_consumption = null;

        if (
            caloriesConsumed !== null &&
            proteinConsumed !== null
        ) {
            current_consumption = {
                calories_kcal: caloriesConsumed,
                protein_g: proteinConsumed
            };
        }

        const caloriesRemaining = numOrZero(
            document.getElementById("caloriesRemaining")?.value
        );

        const proteinRemaining = numOrZero(
            document.getElementById("proteinRemaining")?.value
        );

        let remaining_nutrients = null;

        if (
            caloriesRemaining !== null &&
            proteinRemaining !== null
        ) {
            remaining_nutrients = {
                calories_kcal: caloriesRemaining,
                protein_g: proteinRemaining
            };
        }

        const preferred = parseList(
            document.getElementById("preferredFoods")?.value || ""
        );

        let preferences = null;

        if (preferred.length) {
            preferences = {
                preferred_foods: preferred
            };
        }

        const avoided = parseList(
            document.getElementById("avoidedFoods")?.value || ""
        );

        const unavailable = parseList(
            document.getElementById("unavailableFoods")?.value || ""
        );

        const allergies = parseList(
            document.getElementById("allergies")?.value || ""
        );

        let restrictions = null;

        if (avoided.length || unavailable.length || allergies.length) {
            restrictions = {
                avoided_foods: avoided,
                unavailable_foods: unavailable,
                allergies: allergies
            };
        }

        const age = numOrNull(
            document.getElementById("age")?.value
        );

        const sex =
            document.getElementById("sex")?.value || null;

        const weightKg = numOrNull(
            document.getElementById("weightKg")?.value
        );

        const heightCm = numOrNull(
            document.getElementById("heightCm")?.value
        );

        let user_profile = null;

        if (
            age !== null &&
            sex &&
            weightKg !== null &&
            heightCm !== null
        ) {
            user_profile = {
                age,
                sex,
                weight_kg: weightKg,
                height_cm: heightCm
            };
        }

        const contextParts = {
            user_profile,
            goals,
            current_consumption,
            remaining_nutrients,
            preferences,
            restrictions
        };

        const hasContext = Object.values(contextParts).some(
            (value) => value !== null
        );

        const nutritional_context = hasContext
            ? contextParts
            : null;

        return {
            message,
            session_id: currentSessionId || null,
            nutritional_context
        };
    }

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

    if (errorMessage) {
      errorMessage.textContent = message;
    }
  }

  function setLoading(isLoading) {
    if (btnSubmit) {
      btnSubmit.disabled = isLoading;
      btnSubmit.classList.toggle("is-loading", isLoading);
    }

    function setLoading(isLoading) {
        if (btnSubmit) {
            btnSubmit.disabled = isLoading;
            btnSubmit.classList.toggle("is-loading", isLoading);
        }

        if (stateLoading) {
            stateLoading.hidden = !isLoading;
        }

        if (isLoading && stateError) {
            stateError.hidden = true;
        }
    }

    function updateSessionUI() {
        if (!sessionBadge) return;

        if (currentSessionId) {
            const short = currentSessionId.slice(0, 8) + "…";

            sessionBadge.textContent = short;
            sessionBadge.title = currentSessionId;

            if (btnClearSession) {
                btnClearSession.disabled = false;
            }
        } else {
            sessionBadge.textContent = "Sin sesión";
            sessionBadge.title = "";

            if (btnClearSession) {
                btnClearSession.disabled = true;
            }
        }
    }

    function appendMessage(role, content, options = {}) {
        showChat();

        const { imageDataUrl = null, visionResult = null } = options;

        conversation.push({
            role,
            content,
            imageDataUrl,
            visionResult
        });

        const row = document.createElement("div");
        row.className = `kora-msg kora-msg--${role}`;

        const avatar = document.createElement("div");
        avatar.className = "kora-msg__avatar";

        if (role === "assistant") {
            avatar.innerHTML =
                '<img src="images/k.svg" alt="Kora" width="28" height="28" />';
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
                textDiv.innerHTML = DOMPurify.sanitize(
                    marked.parse(content)
                );

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

        if (messagesList) {
            messagesList.appendChild(row);
        }

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
        const predictions = Array.isArray(result.predictions)
            ? result.predictions
            : [];
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
        header.innerHTML = `<span class="kora-vision-card__title">${titleText}</span>
            <span class="kora-vision-card__status ${statusClass}">${status}</span>`;

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

                const scoreLabel =
                    score !== null
                        ? `puntuación relativa: ${score.toFixed(3)}`
                        : "";

                li.innerHTML = `<strong>${escapeHtml(food)}</strong>${
                    scoreLabel
                        ? ` <span class="kora-vision-card__score">(${scoreLabel})</span>`
                        : ""
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

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function clearConversation() {
        conversation = [];

        if (messagesList) {
            messagesList.innerHTML = "";
        }

        showEmpty();
  function clearConversation() {
    conversation = [];
    if (messagesList) messagesList.innerHTML = "";
    showEmpty();
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

    conversations.forEach((conversationItem) => {
      const button = document.createElement("button");

      button.type = "button";
      button.className = "kora-recent-item";
      button.textContent = conversationItem.title;
      button.dataset.conversationId = conversationItem.id;

      button.addEventListener("click", async () => {
        currentConversationId = conversationItem.id;

        recentChats
          .querySelectorAll(".kora-recent-item")
          .forEach((item) => {
            item.classList.remove("is-active");
          });

        button.classList.add("is-active");
        const currentUserId = localStorage.getItem(USER_ID_STORAGE_KEY);

        if (!currentUserId) return;

        showHistoryLoading();

        try {
          const history = await loadConversationHistory(
            currentUserId,
            currentConversationId
          );

          renderConversationMessages(history.messages || []);
        } catch (error) {
          console.log("Failed to load conversation history:", error);

          showHistoryError(
            "No se pudo cargar el historial. Verifica que svc-management esté disponible."
          );
        }
      });

      recentChats.appendChild(button);
    });
  }

  function renderConversationMessages(messages) {
    clearConversation();

    if (!messages.length) {
      showEmpty();

      if (errorMessage) {
        errorMessage.textContent = "";
      }

      return;
    }

    messages.forEach((message) => {
      appendMessage(message.role, message.content);
    });
  }

  // ---------- API ----------
  async function loadConversations(userId) {
    if (!userId) return [];

    const url = `${CONVERSATIONS_URL}?user_id=${encodeURIComponent(userId)}`;

    const res = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    let data = null;

    try {
      data = await res.json();
    } catch {
      data = null;
    }

    if (!res.ok) {
      const detail = (data && (data.error || data.detail || data.message)) || `HTTP error ${res.status}`;
      throw new Error(
        typeof detail === "string" ? detail : JSON.stringify(detail)
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

    let data = null;

    try {
      data = await res.json();
    } catch {
      data = null;
    }

    if (!res.ok) {
      const detail =
        (data && (data.error || data.detail || data.message)) ||
        `HTTP error ${res.status}`;

        throw new Error(
          typeof detail === "string" ? detail : JSON.stringify(detail)
        );
    }

    return data;
  }

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
          ? `No se pudo conectar con svc-agente (${AGENT_API_BASE}). ¿Está en ejecución?`
          : err.message || "Error desconocido";
      if (errorMessage) errorMessage.textContent = msg;
      if (stateError) stateError.hidden = false;
      // keep the user message visible
      showChat();
    } finally {
      setLoading(false);
    }

    /*
    =====================
    ====================
     */

        async function sendQuery(payload, isRetry = false, imageMeta = null) {
        setLoading(true);
        lastPayload = payload;
        lastImage = imageMeta;

        
    if (!isRetry) {
        appendMessage("user", payload.message, {
            imageDataUrl: imageMeta ? imageMeta.dataUrl : null
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
            const body = new FormData();

            body.append("message", payload.message || "");
            body.append("session_id", payload.session_id || "");
            body.append(
                "nutritional_context",
                payload.nutritional_context
                    ? JSON.stringify(payload.nutritional_context)
                    : ""
            );

            if (imageMeta && imageMeta.file) {
                body.append(
                    "image",
                    imageMeta.file,
                    imageMeta.name || imageMeta.file.name || "image.jpg"
                );
            }

            const res = await fetch(QUERY_URL, {
                method: "POST",
                headers: {
                    Accept: "application/json"
                },
                body
            });

            let data = null;

            try {
                data = await res.json();
            } catch (_) {}

            if (!res.ok) {
                const detail =
                    (data && (data.detail || data.message)) ||
                    `Error HTTP ${res.status}`;

                throw new Error(
                    typeof detail === "string"
                        ? detail
                        : JSON.stringify(detail)
                );
            }

            const text = data.response ?? "";

            if (data.session_id) {
                currentSessionId = data.session_id;
                updateSessionUI();
            }

            const visionResult = data.vision_result || null;

            appendMessage("assistant", text, { visionResult });

            lastPayload = null;
            lastImage = null;

            if (window.clearSelectedImage) {
                window.clearSelectedImage();
            }

        } catch (err) {
            const msg =
                err.name === "TypeError"
                    ? `No se pudo conectar con svc-agente (${API_BASE}). ¿Está en ejecución?`
                    : err.message || "Error desconocido";

            if (errorMessage) {
                errorMessage.textContent = msg;
            }

            if (stateError) {
                stateError.hidden = false;
            }

            showChat();

        } finally {
            setLoading(false);
        }
    }

        
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
                    dataUrl: imageData.dataUrl
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
                    `${API_BASE}/agent/memory/${encodeURIComponent(currentSessionId)}`,
                    {
                        method: "DELETE"
                    }
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
            updateSessionUI();
            clearConversation();

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

        messageInput.style.height =
            Math.min(messageInput.scrollHeight, 160) + "px";
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

    loadContextFromStorage();
    updateSessionUI();
    showEmpty();

})();
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

  const currentUserId = localStorage.getItem(USER_ID_STORAGE_KEY);

  if (currentUserId) {
    loadConversations(currentUserId)
      .then((conversations) => {
        renderConversations(conversations);
      })
      .catch((error) => {
        console.log("Failed to load conversations:", error);

        if (recentChats) {
          recentChats.innerHTML = "";

          const errorItem = document.createElement("p");
          errorItem.className = "kora-sidebar__empty";
          errorItem.textContent = "No se pudieron cargar las conversaciones.";

          recentChats.appendChild(errorItem);
        }
      });
  }
  })();
