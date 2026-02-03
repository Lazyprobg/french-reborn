// ==============================
// ELEMENTS DOM
// ==============================
const messagesContainer = document.getElementById("messages-container");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const emojiButton = document.getElementById("emoji-button");

// ==============================
// AJOUT MESSAGE
// ==============================
function addMessage(username, text){
    const div = document.createElement("div");
    div.className = "message";
    div.innerHTML = `<b>${username}</b> : ${text}`;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ==============================
// CHARGEMENT DES MESSAGES
// ==============================
function loadMessages(){
    fetch("/messages")
        .then(res => res.json())
        .then(data => {
            messagesContainer.innerHTML = "";
            data.forEach(m => {
                addMessage(m.username, m.content);
            });
        });
}

// ==============================
// ENVOI MESSAGE
// ==============================
function sendMessage(){
    const text = input.value.trim();
    if(!text) return;

    fetch("/send", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({content: text})
    });

    input.value = "";
}

// ==============================
// EVENTS
// ==============================
sendButton.addEventListener("click", sendMessage);

input.addEventListener("keypress", e => {
    if(e.key === "Enter"){
        e.preventDefault();
        sendMessage();
    }
});

emojiButton.addEventListener("click", () => {
    const emojis = ["😀","😂","😍","😎","👍","💙","🚀","🔥"];
    const chosen = prompt("Choisis un emoji :\n" + emojis.join(" "));
    if(chosen){
        input.value += chosen;
        input.focus();
    }
});

// ==============================
// AUTO REFRESH
// ==============================
setInterval(loadMessages, 1500);
loadMessages();
