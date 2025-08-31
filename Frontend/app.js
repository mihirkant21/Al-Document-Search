// ====== Elements ======
const inputBox = document.getElementById("input_box");
const sendBtn = document.querySelector(".searchicon_img");
const micBtn = document.getElementById("mic_btn");
const uploadBtn = document.getElementById("pdf_upload");  // FIXED ID
const chatMessages = document.getElementById("chat_messages");

// ====== Send Message Function ======
function sendMessage() {
    const text = inputBox.value.trim();
    if (text === "") return;

    addMessage(text, "user");
    inputBox.value = "";

    // Call FastAPI backend
    fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: text })
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.answer || "⚠️ No response from backend", "bot");
    })
    .catch(err => {
        console.error(err);
        addMessage("❌ Error connecting to backend", "bot");
    });
}


// ====== Input events ======
// Enter key
inputBox.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

// Search icon click
sendBtn.addEventListener("click", () => {
    sendMessage();
});

// ====== Mic Input ======
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        addMessage("🎤 Listening...", "bot");
        micBtn.style.filter = "invert(34%) sepia(89%) saturate(7483%) hue-rotate(358deg)";
    };

    recognition.onresult = (event) => {
        const speechText = event.results[0][0].transcript;
        inputBox.value = speechText;
        sendMessage();
    };

    recognition.onerror = (event) => {
        addMessage("❌ Mic error: " + event.error, "bot");
    };

    recognition.onend = () => {
        micBtn.style.filter = "";
    };

    micBtn.addEventListener("click", () => {
        recognition.start();
    });
} else {
    micBtn.addEventListener("click", () => {
        addMessage("❌ Speech Recognition not supported in this browser", "bot");
    });
}

// ====== Upload PDF ======
// ====== Upload PDF ======
uploadBtn.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) {
        addMessage(`📂 Uploading: ${file.name}`, "user");

        const formData = new FormData();
        formData.append("file", file);

        fetch("http://127.0.0.1:8000/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.message || "✅ PDF uploaded successfully!", "bot");
        })
        .catch(err => {
            console.error(err);
            addMessage("❌ Failed to upload PDF", "bot");
        });
    }
});


// ====== Add Message Function ======
function addMessage(text, type) {
    const msg = document.createElement("div");
    msg.classList.add("chat-message", type);
    msg.innerText = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
