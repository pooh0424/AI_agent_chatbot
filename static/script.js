document.addEventListener("DOMContentLoaded", async () => {
    const chatHistory = document.getElementById("chat-history");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const fileInput = document.getElementById("file-input");
    const sessionStatus = document.getElementById("session-status");
    const sendBtn = document.getElementById("send-btn");

    const systemPromptInput = document.getElementById("system-prompt-input");
    const newSessionBtn = document.getElementById("new-session-btn");
    const filePreviewContainer = document.getElementById("file-preview-container");
    const filePreviewName = document.getElementById("file-preview-name");
    const removeFileBtn = document.getElementById("remove-file-btn");

    let sessionId = null;

    // 3. UI Helper to append messages
    function appendMessage(role, content, filePath = null) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", role);

        if (filePath) {
            // Re-route the local file path to the FastAPI static /uploads mount
            const normalizedPath = filePath.replace('./uploads', '/uploads').replace(/\\/g, '/');
            const imgEl = document.createElement("img");
            imgEl.src = normalizedPath;
            imgEl.classList.add("message-img");
            imgEl.alt = "Uploaded content";
            msgDiv.appendChild(imgEl);
        }

        if (content) {
            const textSpan = document.createElement("span");
            // Basic markdown handling for bold text that Gemini often uses
            textSpan.innerHTML = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
            msgDiv.appendChild(textSpan);
        }

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Auto-scroll
    }

    // 1. Initialize Session
    async function initSession(systemPrompt = "") {
        try {
            sessionStatus.textContent = "Connecting...";
            const payload = systemPrompt ? { system_prompt: systemPrompt } : {};

            const res = await fetch("/sessions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("Failed to create session");
            const data = await res.json();
            sessionId = data.id;
            sessionStatus.textContent = `Session #${sessionId} Active`;
            chatHistory.innerHTML = ''; // Clear chat history for new session
        } catch (err) {
            console.error(err);
            sessionStatus.textContent = "Error: Could not connect to API";
            sendBtn.disabled = true;
        }
    }

    // Call init on load
    await initSession();

    // Handle New Session Button Click
    newSessionBtn.addEventListener("click", async () => {
        newSessionBtn.disabled = true;
        const promptValue = systemPromptInput.value.trim();
        await initSession(promptValue);
        newSessionBtn.disabled = false;
    });

    // 2. Handle File Selection Preview
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            filePreviewName.textContent = fileInput.files[0].name;
            filePreviewContainer.classList.remove("hidden");
        } else {
            filePreviewContainer.classList.add("hidden");
        }
    });

    removeFileBtn.addEventListener("click", () => {
        fileInput.value = ""; // Clear file
        filePreviewContainer.classList.add("hidden");
    });

    // 4. Handle Form Submission
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!sessionId) return;

        const content = messageInput.value.trim();
        const file = fileInput.files[0];

        if (!content && !file) return;

        // Optimistically show user message
        const tempPath = file ? URL.createObjectURL(file) : null;
        // For temporary frontend preview, pretend the tempPath is the final image
        appendMessage("user", content, tempPath);

        // Prepare Frontend State
        messageInput.value = "";
        fileInput.value = "";
        filePreviewContainer.classList.add("hidden");
        sendBtn.disabled = true;
        sessionStatus.textContent = "AI is thinking...";

        // Build Payload
        const formData = new FormData();
        if (content) formData.append("content", content);
        if (file) formData.append("file", file);

        try {
            const res = await fetch(`/sessions/${sessionId}/chat`, {
                method: "POST",
                body: formData
            });

            if (!res.ok) throw new Error("API returned an error");

            const aiData = await res.json();
            appendMessage("model", aiData.content, aiData.file_path);
            sessionStatus.textContent = `Session #${sessionId} Active`;
        } catch (err) {
            console.error(err);
            appendMessage("model", "⚠️ Error: Unable to reach the AI model.");
            sessionStatus.textContent = `Session #${sessionId} Active (Error last request)`;
        } finally {
            sendBtn.disabled = false;
        }
    });
});
