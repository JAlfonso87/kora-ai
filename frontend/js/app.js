
(function () {
  "use strict";

  const API_BASE = "http://localhost:8000";
  const QUERY_URL = `${API_BASE}/agent/query`;

  const form = document.getElementById("queryForm");
  const btnSubmit = document.getElementById("btnSubmit");
  const btnFillExample = document.getElementById("btnFillExample");
  const btnClearSession = document.getElementById("btnClearSession");
  const btnRetry = document.getElementById("btnRetry");
  const sessionBadge = document.getElementById("sessionBadge");
  const apiBaseLabel = document.getElementById("apiBaseLabel");

  const stateEmpty = document.getElementById("stateEmpty");
  const stateLoading = document.getElementById("stateLoading");
  const stateError = document.getElementById("stateError");
  const stateSuccess = document.getElementById("stateSuccess");
  const errorMessage = document.getElementById("errorMessage");
  const responseText = document.getElementById("responseText");
  const responseSession = document.getElementById("responseSession");

  apiBaseLabel.textContent = API_BASE;

  let currentSessionId = null;
  let lastPayload = null;


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

  function buildPayload() {
    const message = document.getElementById("message").value.trim();

    const primary = document.getElementById("goalPrimary").value || null;
    const calorieTarget = numOrNull(document.getElementById("calorieTarget").value);
    const proteinTarget = numOrNull(document.getElementById("proteinTarget").value);
    let goals = null;
    if (primary && calorieTarget !== null && proteinTarget !== null) {
      goals = {
        primary,
        calorie_target_kcal: calorieTarget,
        protein_target_g: proteinTarget,
      };
    }

    const caloriesConsumed = numOrZero(document.getElementById("caloriesConsumed").value);
    const proteinConsumed = numOrZero(document.getElementById("proteinConsumed").value);
    let current_consumption = null;
    if (caloriesConsumed !== null && proteinConsumed !== null) {
      current_consumption = {
        calories_kcal: caloriesConsumed,
        protein_g: proteinConsumed,
      };
    }

    const caloriesRemaining = numOrZero(document.getElementById("caloriesRemaining").value);
    const proteinRemaining = numOrZero(document.getElementById("proteinRemaining").value);
    let remaining_nutrients = null;
    if (caloriesRemaining !== null && proteinRemaining !== null) {
      remaining_nutrients = {
        calories_kcal: caloriesRemaining,
        protein_g: proteinRemaining,
      };
    }

    const preferred = parseList(document.getElementById("preferredFoods").value);
    let preferences = null;
    if (preferred.length) {
      preferences = { preferred_foods: preferred };
    }

    const avoided = parseList(document.getElementById("avoidedFoods").value);
    const unavailable = parseList(document.getElementById("unavailableFoods").value);
    const allergies = parseList(document.getElementById("allergies").value);
    let restrictions = null;
    if (avoided.length || unavailable.length || allergies.length) {
      restrictions = {
        avoided_foods: avoided,
        unavailable_foods: unavailable,
        allergies: allergies,
      };
    }

    const age = numOrNull(document.getElementById("age").value);
    const sex = document.getElementById("sex").value || null;
    const weightKg = numOrNull(document.getElementById("weightKg").value);
    const heightCm = numOrNull(document.getElementById("heightCm").value);
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

    const payload = {
      message,
      session_id: currentSessionId || null,
      nutritional_context,
    };

    return payload;
  }

  function showState(name) {
    stateEmpty.hidden = name !== "empty";
    stateLoading.hidden = name !== "loading";
    stateError.hidden = name !== "error";
    stateSuccess.hidden = name !== "success";
  }

  function setLoading(isLoading) {
    btnSubmit.disabled = isLoading;
    btnSubmit.classList.toggle("is-loading", isLoading);
    if (isLoading) {
      showState("loading");
    }
  }

  function updateSessionUI() {
    if (currentSessionId) {
      const short = currentSessionId.slice(0, 8) + "…";
      sessionBadge.textContent = short;
      sessionBadge.title = currentSessionId;
      btnClearSession.disabled = false;
    } else {
      sessionBadge.textContent = "Sin sesión";
      sessionBadge.title = "";
      btnClearSession.disabled = true;
    }
  }

  async function sendQuery(payload) {
    setLoading(true);
    lastPayload = payload;

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

      responseText.textContent = text;
      responseSession.textContent = data.session_id
        ? `sesión: ${data.session_id.slice(0, 8)}…`
        : "";
      showState("success");
    } catch (err) {
      const msg =
        err.name === "TypeError"
          ? `No se pudo conectar con svc-agente (${API_BASE}). ¿Está en ejecución?`
          : err.message || "Error desconocido";
      errorMessage.textContent = msg;
      showState("error");
    } finally {
      setLoading(false);
    }
  }


  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const payload = buildPayload();

    if (!payload.message) {
      errorMessage.textContent = "El mensaje no puede estar vacío.";
      showState("error");
      document.getElementById("message").focus();
      return;
    }

    sendQuery(payload);
  });

  btnRetry.addEventListener("click", () => {
    if (lastPayload) {
      sendQuery(lastPayload);
    } else {
      form.requestSubmit();
    }
  });

  btnClearSession.addEventListener("click", async () => {
    if (!currentSessionId) return;

    try {
      await fetch(`${API_BASE}/agent/memory/${encodeURIComponent(currentSessionId)}`, {
        method: "DELETE",
      });
    } catch {
    }

    currentSessionId = null;
    updateSessionUI();
    showState("empty");
    responseText.textContent = "";
  });

  btnFillExample.addEventListener("click", () => {
    document.getElementById("message").value =
      "¿Qué puedo comer para completar la proteína restante de hoy?";
    document.getElementById("goalPrimary").value = "weight_loss";
    document.getElementById("calorieTarget").value = "2000";
    document.getElementById("proteinTarget").value = "120";
    document.getElementById("caloriesConsumed").value = "1550";
    document.getElementById("proteinConsumed").value = "75";
    document.getElementById("caloriesRemaining").value = "450";
    document.getElementById("proteinRemaining").value = "45";
    document.getElementById("preferredFoods").value = "pollo, arroz, verduras";
    document.getElementById("avoidedFoods").value = "pescado";
    document.getElementById("allergies").value = "";
    document.getElementById("unavailableFoods").value = "";
    document.getElementById("age").value = "28";
    document.getElementById("sex").value = "male";
    document.getElementById("weightKg").value = "72";
    document.getElementById("heightCm").value = "175";
  });

  updateSessionUI();
  showState("empty");
})();
