(function () {
  const chat       = document.getElementById("chatContainer");
  const context    = document.getElementById("contextPanel");
  const composer   = document.getElementById("chatComposer");
  const btnContext = document.getElementById("btnOpenContext");
  const btnChat    = document.getElementById("btnNewChat");

  if (!chat || !context || !composer || !btnContext) return;

  let formLoaded = false;

  async function loadContextForm() {
    if (formLoaded) return;

    try {
      const res = await fetch("context-form.html");
      if (!res.ok) throw new Error("No se pudo cargar el formulario");
      const html = await res.text();
      context.innerHTML = html;
      formLoaded = true;
      initContextLogic();
    } catch (err) {
      context.innerHTML = `
        <div style="padding: 2rem; color: #c00;">
          <p>Error al cargar el formulario de contexto nutricional.</p>
          <p style="font-size: 0.9em; opacity: 0.8;">${err.message}</p>
        </div>`;
      console.error(err);
    }
  }

  function openContext() {
    chat.hidden = true;
    composer.hidden = true;
    context.hidden = false;
    loadContextForm();
  }

  function openChat() {
    context.hidden = true;
    chat.hidden = false;
    composer.hidden = false;
  }

  btnContext.addEventListener("click", openContext);
  btnChat.addEventListener("click", openChat);

  
  function initContextLogic() {
    const STORAGE_KEY = "kora_nutritional_context";

    const fields = [
      "goalPrimary", "calorieTarget", "proteinTarget",
      "caloriesConsumed", "proteinConsumed",
      "caloriesRemaining", "proteinRemaining",
      "preferredFoods", "avoidedFoods", "allergies", "unavailableFoods",
      "age", "sex", "weightKg", "heightCm"
    ];

    function load() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        const data = JSON.parse(raw);
        fields.forEach((id) => {
          const el = document.getElementById(id);
          if (el && data[id] !== undefined && data[id] !== null) {
            el.value = data[id];
          }
        });
      } catch (_) {}
    }

    function save() {
      const data = {};
      fields.forEach((id) => {
        const el = document.getElementById(id);
        data[id] = el ? el.value : "";
      });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));

      const status = document.getElementById("contextStatus");
      if (status) {
        status.hidden = false;
        status.textContent = "Contexto guardado. Se usará en las próximas consultas del chat.";
        status.className = "kora-context-status is-ok";
        setTimeout(() => { status.hidden = true; }, 3500);
      }
    }

    function clear() {
      fields.forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });
      localStorage.removeItem(STORAGE_KEY);

      const status = document.getElementById("contextStatus");
      if (status) {
        status.hidden = false;
        status.textContent = "Contexto eliminado.";
        status.className = "kora-context-status";
        setTimeout(() => { status.hidden = true; }, 2500);
      }
    }

    document.getElementById("btnSaveContext")?.addEventListener("click", save);
    document.getElementById("btnClearContext")?.addEventListener("click", clear);

    document.getElementById("btnFillExample")?.addEventListener("click", () => {
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

    load();
  }
})();