const MAX_CHARS = 1000;

const textarea = document.getElementById("note-content");
const counter = document.getElementById("char-counter");

function updateCounter() {
    const length = textarea.value.length;
    counter.textContent = `${length}/${MAX_CHARS}`;

    counter.classList.remove("counter-warning", "counter-danger");
    if (length >= MAX_CHARS) {
        counter.classList.add("counter-danger");
    } else if (length >= 900) {
        counter.classList.add("counter-warning");
    }
}

if (textarea && counter) {
    textarea.addEventListener("input", updateCounter);
    updateCounter();
}

const ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp", "pdf"];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

const attachmentInput = document.getElementById("attachment");
const attachmentName = document.getElementById("attachment-name");

if (attachmentInput && attachmentName) {
    attachmentInput.addEventListener("change", () => {
        const file = attachmentInput.files[0];
        attachmentName.classList.remove("attachment-error");

        if (!file) {
            attachmentName.textContent = "";
            return;
        }

        const extension = file.name.split(".").pop().toLowerCase();

        if (!ALLOWED_EXTENSIONS.includes(extension)) {
            attachmentName.textContent = "Solo se permiten imágenes (jpg, png, gif, webp) o archivos PDF.";
            attachmentName.classList.add("attachment-error");
            attachmentInput.value = "";
            return;
        }

        if (file.size > MAX_FILE_SIZE) {
            attachmentName.textContent = "El archivo adjunto no puede superar los 5MB.";
            attachmentName.classList.add("attachment-error");
            attachmentInput.value = "";
            return;
        }

        attachmentName.textContent = `📎 ${file.name}`;
    });
}
