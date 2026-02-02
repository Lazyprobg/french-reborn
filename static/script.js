const messagesContainer = document.getElementById("messages");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

let lastMessageDate = null;

// Fonction format date/heure
function formatDate(date) {
    return date.toLocaleDateString("fr-FR") + " " +
           date.toLocaleTimeString("fr-FR", {
               hour: "2-digit",
               minute: "2-digit"
           });
}

function sameMinute(d1, d2) {
    return d1 &&
        d1.getFullYear() === d2.getFullYear() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getDate() === d2.getDate() &&
        d1.getHours() === d2.getHours() &&
        d1.getMinutes() === d2.getMinutes();
}

function addMessage(username, role, text) {
    const now = new Date();

    // Affichage date si différente
    if (!sameMinute(lastMessageDate, now)) {
        const dateDiv = document.createElement("div");
        dateDiv.className = "message-date";
        dateDiv.textContent = formatDate(now);
        messagesContainer.appendChild(dateDiv);
    }

    lastMessageDate = now;

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
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Envoi message
sendButton.addEventListener("click", () => {
    const text = input.value.trim();
    if (!text) return;

    // TEMPORAIRE (plus tard backend)
    addMessage(CURRENT_USER, CURRENT_ROLE, text);
    input.value = "";
});

// Envoi avec Entrée
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendButton.click();
    }
});
