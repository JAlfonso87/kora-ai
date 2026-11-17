
(function () {
    "use strict";

    const btnAddImage = document.getElementById("btnAddImage");
    const imageInput = document.getElementById("imageInput");
    const imagePreview = document.getElementById("imagePreview");
    const previewImg = document.getElementById("previewImg");
    const btnRemoveImage = document.getElementById("btnRemoveImage");

    let selectedFile = null;

    const VALID_TYPES = ["image/jpeg", "image/png"];
    const VALID_EXTENSIONS = [".jpg", ".jpeg", ".png"];
    const MAX_SIZE_BYTES = 10 * 1024 * 1024;

    if (!btnAddImage || !imageInput) return;

    function showValidationError(message) {
        const errorMessage = document.getElementById("errorMessage");
        const stateError = document.getElementById("stateError");

        if (errorMessage) {
            errorMessage.textContent = message;
        }

        if (stateError) {
            stateError.hidden = false;
        }
    }

    function hideValidationError() {
        const stateError = document.getElementById("stateError");

        if (stateError) {
            stateError.hidden = true;
        }
    }

    btnAddImage.addEventListener("click", () => {
        imageInput.click();
    });

    imageInput.addEventListener("change", (e) => {
        const file = e.target.files[0];

        if (!file) return;

        if (!VALID_TYPES.includes(file.type)) {
            const name = (file.name || "").toLowerCase();

            const hasValidExt = VALID_EXTENSIONS.some((ext) =>
                name.endsWith(ext)
            );

            if (!hasValidExt) {
                showValidationError(
                    "Formato no válido. Solo se permiten fotografías JPG o PNG. Elige otra imagen."
                );

                imageInput.value = "";
                return;
            }
        }

        if (file.size > MAX_SIZE_BYTES) {
            showValidationError(
                "La imagen es demasiado grande (máximo 10 MB). Comprime la fotografía o elige otra."
            );

            imageInput.value = "";
            return;
        }

        if (file.size === 0) {
            showValidationError(
                "El archivo está vacío. Selecciona una fotografía válida."
            );

            imageInput.value = "";
            return;
        }

        hideValidationError();
        selectedFile = file;

        const reader = new FileReader();

        reader.onload = (ev) => {
            previewImg.src = ev.target.result;
            imagePreview.hidden = false;

            btnAddImage.classList.add("has-image");
            btnAddImage.setAttribute("title", "Cambiar imagen");
            btnAddImage.setAttribute("aria-label", "Cambiar imagen");
        };

        reader.onerror = () => {
            showValidationError(
                "No se pudo leer la imagen. Intenta con otro archivo."
            );

            clearImage();
        };

        reader.readAsDataURL(file);
    });

    if (btnRemoveImage) {
        btnRemoveImage.addEventListener("click", () => {
            clearImage();
            hideValidationError();
        });
    }

    function clearImage() {
        selectedFile = null;
        imageInput.value = "";
        previewImg.src = "";
        imagePreview.hidden = true;

        btnAddImage.classList.remove("has-image");
        btnAddImage.setAttribute("title", "Añadir imagen");
        btnAddImage.setAttribute("aria-label", "Añadir imagen");
    }

    window.getSelectedImage = function () {
        return selectedFile;
    };

    window.clearSelectedImage = function () {
        clearImage();
    };

    window.getSelectedImageAsBase64 = function () {
        return new Promise((resolve) => {
            if (!selectedFile) {
                resolve(null);
                return;
            }

            const file = selectedFile;
            const reader = new FileReader();

            reader.onload = (ev) => {
                resolve({
                    file: file,
                    dataUrl: ev.target.result,
                    mime: file.type || "image/jpeg",
                    name: file.name || "photo.jpg",
                    size: file.size
                });
            };

            reader.onerror = () => {
                resolve(null);
            };

            reader.readAsDataURL(file);
        });
    };

})();
