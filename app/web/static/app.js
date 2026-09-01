// Frontend chat script (cleaned and improved)
const form = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send-button");
const messages = document.getElementById("messages");
const errorMessage = document.getElementById("error-message");
const appVersionEl = document.getElementById("app-version");

let sessionId = localStorage.getItem("app_session_id") || null;

// Optionally set version if needed (keeps default 1.0 if not provided)
if (window.APP_VERSION) {
  appVersionEl.textContent = window.APP_VERSION;
}

function formatTime(date = new Date()) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(role, content, sources = [], messageId = null, time = null) {
  const wrapper = document.createElement("div");
  wrapper.className = "message-wrapper";

  const message = document.createElement("div");
  message.className = `message ${role}`;
  // message.textContent = content;
  if (role === "assistant" && (!sources || sources.length === 0)) {
    const notice = document.createElement("strong");
    notice.className = "ai-notice";
    notice.textContent = "No relevant document content found. Answer generated using general AI knowledge.";
    message.appendChild(notice);
  }

  const answerText = document.createElement("div");
  answerText.textContent = content;
  message.appendChild(answerText);

  wrapper.appendChild(message);

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = time ? formatTime(new Date(time)) : formatTime();
  message.appendChild(meta);


  if (sources && sources.length > 0) {
    const sourceBox = document.createElement("div");
    sourceBox.className = "sources";

    sourceBox.innerHTML = `
  <strong>Sources: </strong>
  <div>${sources.map((source) =>
      `${source.document_name} | Relevance: ${(source.similarity * 100).toFixed(1)}%`
    ).join("<br>")}</div>
`;

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

function showLoading() {
  const loadingWrapper = document.createElement("div");
  loadingWrapper.className = "message-wrapper";
  loadingWrapper.id = "loading-message";

  const loadingMessage = document.createElement("div");
  loadingMessage.className = "message assistant";
  loadingMessage.textContent = "Searching the app knowledge base...";
  loadingWrapper.appendChild(loadingMessage);

  messages.appendChild(loadingWrapper);
  messages.scrollTop = messages.scrollHeight;
}

async function sendQuestion(question) {
  errorMessage.textContent = "";
  sendButton.disabled = true;
  questionInput.disabled = true;

  addMessage("user", question, [], null);

  showLoading();

  try {
    const response = await fetch("/api/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, session_id: sessionId }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || "Unable to get an answer.");
    }

    sessionId = data.session_id;
    localStorage.setItem("app_session_id", sessionId);

    document.getElementById("loading-message")?.remove();

    addMessage("assistant", data.answer || "No answer returned.", data.sources || [], data.message_id || null, data.timestamp || null);
  } catch (error) {
    document.getElementById("loading-message")?.remove();
    errorMessage.textContent = error.message || "Something went wrong.";
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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_id: messageId, rating: rating }),
    });

    if (!response.ok) throw new Error("Unable to submit feedback.");
    feedbackBox.textContent = "Thank you for your feedback.";
  } catch (err) {
    errorMessage.textContent = err.message || "Could not submit feedback.";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  questionInput.value = "";
  await sendQuestion(question);
});

// suggestions
document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", async () => {
    const question = button.dataset.question;
    questionInput.value = question;
    // small delay to show input
    setTimeout(() => form.dispatchEvent(new Event("submit", { cancelable: true })), 50);
  });
});

// submit on Enter when not composing
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.dispatchEvent(new Event("submit", { cancelable: true }));
  }
});