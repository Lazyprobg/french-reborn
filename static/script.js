// ==============================
// CONFIGURATION UTILISATEUR
// ==============================
const CURRENT_USER = window.CURRENT_USER || "Utilisateur";
const CURRENT_ROLE = window.CURRENT_ROLE || "Citoyen";

// ==============================
// ELEMENTS DU DOM
// ==============================
const messagesContainer = document.getElementById("messages-container");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const emojiButton = document.getElementById("emoji-button");

// Pour contrôler l'affichage des dates
let lastMessageDate = null;

// ==============================
// FONCTIONS UTILES
// ==============================

// Formatage date HH:MM / DD/MM/YYYY
function formatDate(date) {
    const d = date.getDate().toString().padStart(2, "0");
    const m = (date.getMonth() + 1).toString().padStart(2, "0");
    const y = date.getFullYear();

    const h = date.getHours().toString().padStart(2, "0");
    const min = date.getMinutes().toString().padStart(2, "0");

    return `${d}/${m}/${y} ${h}:${min}`;
}

// Vérifie si deux dates sont dans la même minute
function sameMinute(d1, d2) {
    if (!d1 || !d2) return false;
    return (
        d1.getFullYear() === d2.getFullYear() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getDate() === d2.getDate() &&
        d1.getHours() === d2.getHours() &&
        d1.getMinutes() === d2.getMinutes()
    );
}

// Ajoute un message au chat
function addMessage(username, role, text, date = new Date()) {
    // Affiche la date si différente de la dernière
    if (!sameMinute(lastMessageDate, date)) {
        const dateDiv = document.createElement("div");
        dateDiv.className = "message-date";
        dateDiv.textContent = formatDate(date);
        messagesContainer.appendChild(dateDiv);
    }

    lastMessageDate = date;

    const messageDiv = document.createElement("div");
    messageDiv.className = "message";

    messageDiv.innerHTML = `
        <div class="avatar"></div>
        <div class="message-content">
            <div class="role">${role}</div>
            <div class="username">${username}</div>
            <div class="text">${text}</div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);

    // Scroll automatique
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ==============================
// CHARGEMENT HISTORIQUE
// ==============================
document.addEventListener("DOMContentLoaded", () => {
    fetch("/messages")
        .then(res => res.json())
        .then(data => {
            data.forEach(msg => {
                addMessage(
                    msg.username,
                    msg.role,
                    msg.content,
                    new Date(msg.timestamp)
                );
            });
        });
});

// ==============================
// ENVOI MESSAGE
// ==============================
sendButton.addEventListener("click", () => {
    const text = input.value.trim();
    if (!text) return;

    fetch("/send_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            addMessage(CURRENT_USER, CURRENT_ROLE, text);
            input.value = "";
        }
    });
});

// Envoi avec la touche Enter
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendButton.click();
    }
});

// ==============================
// GESTION EMOJI (simple)
// ==============================
emojiButton.addEventListener("click", () => {
    const emojiList = ["😀","😂","😍","😎","👍","💙","🚀","✈️"];
    const chosen = prompt("Choisis un emoji:\n" + emojiList.join(" "));
    if (chosen) {
        input.value += chosen;
        input.focus();
    }
});
