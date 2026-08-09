const API_URL = "https://hireme-ai-iivb.onrender.com";

const messages = document.getElementById("messages");
const questionInput = document.getElementById("question");
const sendBtn = document.getElementById("sendBtn");


// =========================
// Send Message
// =========================

async function sendMessage() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    // Remove welcome screen
    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }


    // Show user message
    addMessage("user", question);

    questionInput.value = "";

    sendBtn.disabled = true;


    // Show loading
    const loadingMessage = addMessage(
        "ai",
        "Thinking..."
    );


    try {

        const response = await fetch(
            `${API_URL}/chat`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        if (!response.ok) {
            throw new Error(
                `Server error: ${response.status}`
            );
        }


        const data = await response.json();


        // Replace Thinking...
        loadingMessage.querySelector(
            ".message-content"
        ).textContent = data.answer;


    } catch (error) {

        console.error(error);

        loadingMessage.querySelector(
            ".message-content"
        ).textContent =
            "Sorry, something went wrong. Please try again.";

    }


    sendBtn.disabled = false;

    questionInput.focus();
}


// =========================
// Add Message
// =========================

function addMessage(type, text) {

    const message = document.createElement("div");

    message.className = "message";


    const avatar = document.createElement("div");

    avatar.className =
        "avatar " +
        (type === "user"
            ? "user-avatar"
            : "ai-avatar");

    avatar.textContent =
        type === "user"
            ? "U"
            : "AI";


    const content = document.createElement("div");

    content.className = "message-content";


    if (type === "user") {

        content.className += " user-message";

    }


    content.textContent = text;


    message.appendChild(avatar);

    message.appendChild(content);

    messages.appendChild(message);


    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;


    return message;
}


// =========================
// Suggestion Buttons
// =========================

function askSuggestion(question) {

    questionInput.value = question;

    sendMessage();
}


// =========================
// Enter Key
// =========================

function handleKey(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendMessage();
    }
}


// =========================
// New Chat
// =========================

function newChat() {

    messages.innerHTML = `
        <div class="welcome">

            <div class="welcome-icon">✦</div>

            <h1>How can I help you?</h1>

            <p>
                Ask me anything about the candidate's
                resume, skills, projects or experience.
            </p>

            <div class="suggestions">

                <button onclick="askSuggestion('Tell me about yourself')">
                    Tell me about yourself
                </button>

                <button onclick="askSuggestion('What are your technical skills?')">
                    What are your skills?
                </button>

                <button onclick="askSuggestion('What projects have you worked on?')">
                    Tell me about your projects
                </button>

            </div>

        </div>
    `;

    questionInput.value = "";

    questionInput.focus();
}