const form = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send-button");
const messages = document.getElementById("messages");
const errorMessage = document.getElementById("error-message");

let sessionId = localStorage.getItem("app_session_id");


function addMessage(role, content, sources = [], messageId = null) {
    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper";

    const message = document.createElement("div");
    message.className = `message ${role}`;
    message.textContent = content;

    wrapper.appendChild(message);

    if (sources.length > 0) {
        const sourceBox = document.createElement("div");
        sourceBox.className = "sources";

        const names = sources.map((source) => {
            return `${source.document_name} (${source.similarity})`;
        });

        sourceBox.textContent = `Sources: ${names.join(", ")}`;
        wrapper.appendChild(sourceBox);
    }

    if (role === "assistant" && messageId) {
        const feedback = document.createElement("div");
        feedback.className = "feedback";

        const helpfulButton = document.createElement("button");
        helpfulButton.textContent = "Helpful";

        helpfulButton.addEventListener("click", () => {
            submitFeedback(messageId, 1, feedback);
        });

        const unhelpfulButton = document.createElement("button");
        unhelpfulButton.textContent = "Not helpful";

        unhelpfulButton.addEventListener("click", () => {
            submitFeedback(messageId, -1, feedback);
        });

        feedback.appendChild(helpfulButton);
        feedback.appendChild(unhelpfulButton);
        wrapper.appendChild(feedback);
    }

    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
}


async function sendQuestion(question) {
    errorMessage.textContent = "";
    sendButton.disabled = true;
    questionInput.disabled = true;

    addMessage("user", question);

    const loadingWrapper = document.createElement("div");
    loadingWrapper.className = "message-wrapper";
    loadingWrapper.id = "loading-message";

    const loadingMessage = document.createElement("div");
    loadingMessage.className = "message assistant";
    loadingMessage.textContent = "Searching the app knowledge base...";

    loadingWrapper.appendChild(loadingMessage);
    messages.appendChild(loadingWrapper);

    try {
        const response = await fetch("/api/v1/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                question: question,
                session_id: sessionId,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error?.message || "Unable to get an answer."
            );
        }

        sessionId = data.session_id;

        localStorage.setItem(
            "app_session_id",
            sessionId
        );

        document.getElementById("loading-message")?.remove();

        addMessage(
            "assistant",
            data.answer,
            data.sources,
            data.message_id
        );
    } catch (error) {
        document.getElementById("loading-message")?.remove();
        errorMessage.textContent = error.message;
    } finally {
        sendButton.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
    }
}


async function submitFeedback(messageId, rating, feedbackBox) {
    try {
        const response = await fetch("/api/v1/chat/feedback", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message_id: messageId,
                rating: rating,
            }),
        });

        if (!response.ok) {
            throw new Error("Unable to submit feedback.");
        }

        feedbackBox.textContent = "Thank you for your feedback.";
    } catch (error) {
        errorMessage.textContent = error.message;
    }
}


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    questionInput.value = "";

    await sendQuestion(question);
});


document.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", async () => {
        const question = button.dataset.question;
        await sendQuestion(question);
    });
});