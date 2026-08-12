const loginSection =
    document.getElementById("login-section");

const dashboardSection =
    document.getElementById("dashboard-section");

const loginForm =
    document.getElementById("login-form");

const uploadForm =
    document.getElementById("upload-form");

const documentList =
    document.getElementById("document-list");

const currentUser =
    document.getElementById("current-user");

const adminMessage =
    document.getElementById("admin-message");

const logoutButton =
    document.getElementById("logout-button");

const refreshButton =
    document.getElementById("refresh-button");

let token = localStorage.getItem("admin_token");


function showMessage(message, isError = false) {
    adminMessage.textContent = message;

    adminMessage.className = isError
        ? "admin-message error"
        : "admin-message success";
}


async function apiRequest(url, options = {}) {
    const headers = options.headers || {};

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers: headers,
    });

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data.error?.message ||
            "Request failed."
        );
    }

    return data;
}


async function login(username, password) {
    const data = await apiRequest(
        "/api/v1/auth/login",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,
                password: password,
            }),
        }
    );

    token = data.access_token;

    localStorage.setItem(
        "admin_token",
        token
    );

    await loadCurrentUser();
}


async function loadCurrentUser() {
    try {
        const user = await apiRequest(
            "/api/v1/auth/me"
        );

        currentUser.textContent =
            `${user.username} (${user.role})`;

        loginSection.classList.add("hidden");
        dashboardSection.classList.remove("hidden");

        await loadDocuments();
    } catch (error) {
        logout();
        showMessage(error.message, true);
    }
}


async function loadDocuments() {
    try {
        const documents = await apiRequest(
            "/api/v1/admin/documents"
        );

        documentList.replaceChildren();

        if (documents.length === 0) {
            const row = window.document.createElement("tr");
            const cell = window.document.createElement("td");

            cell.colSpan = 5;
            cell.textContent = "No documents uploaded.";

            row.appendChild(cell);
            documentList.appendChild(row);

            return;
        }

        documents.forEach((item) => {
            const row = window.document.createElement("tr");

            const idCell = window.document.createElement("td");
            idCell.textContent = item.id;

            const nameCell = window.document.createElement("td");
            nameCell.textContent = item.original_name;

            const statusCell = window.document.createElement("td");
            const status = window.document.createElement("span");

            status.className = "status status-" + item.status;
            status.textContent = item.status;
            statusCell.appendChild(status);

            const sizeCell = window.document.createElement("td");
            sizeCell.textContent = formatFileSize(item.file_size);

            const actionCell = window.document.createElement("td");
            actionCell.className = "action-buttons";

            const indexButton = window.document.createElement("button");
            indexButton.textContent = "Index";
            indexButton.addEventListener("click", function () {
                indexDocument(item.id);
            });

            const deleteButton = window.document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.className = "danger-button";
            deleteButton.addEventListener("click", function () {
                deleteDocument(item.id);
            });

            actionCell.appendChild(indexButton);
            actionCell.appendChild(deleteButton);

            row.appendChild(idCell);
            row.appendChild(nameCell);
            row.appendChild(statusCell);
            row.appendChild(sizeCell);
            row.appendChild(actionCell);

            documentList.appendChild(row);
        });
    } catch (error) {
        showMessage(error.message, true);
    }
}


async function uploadDocument(file) {
    const formData = new FormData();

    formData.append("file", file);

    await apiRequest(
        "/api/v1/admin/documents",
        {
            method: "POST",
            body: formData,
        }
    );

    showMessage(
        "Document uploaded. Click Index to add it to the knowledge base."
    );

    await loadDocuments();
}


async function indexDocument(documentId) {
    try {
        const data = await apiRequest(
            `/api/v1/admin/rag/documents/${documentId}/index`,
            {
                method: "POST",
            }
        );

        showMessage(
            `${data.message} Chunks created: ${data.chunks_created}`
        );

        await loadDocuments();
    } catch (error) {
        showMessage(error.message, true);
    }
}


async function deleteDocument(documentId) {
    const shouldDelete = window.confirm(
        "Delete this document and its vector data?"
    );

    if (!shouldDelete) {
        return;
    }

    try {
        const data = await apiRequest(
            `/api/v1/admin/documents/${documentId}`,
            {
                method: "DELETE",
            }
        );

        showMessage(data.message);

        await loadDocuments();
    } catch (error) {
        showMessage(error.message, true);
    }
}


function logout() {
    token = null;

    localStorage.removeItem("admin_token");

    dashboardSection.classList.add("hidden");
    loginSection.classList.remove("hidden");

    currentUser.textContent = "";
}


function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    return `${(bytes / 1024).toFixed(1)} KB`;
}


function escapeHtml(value) {
    const element = document.createElement("div");

    element.textContent = value;

    return element.innerHTML;
}


loginForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const username =
            document.getElementById("username").value.trim();

        const password =
            document.getElementById("password").value;

        try {
            await login(username, password);

            loginForm.reset();

            showMessage("Login successful.");
        } catch (error) {
            showMessage(error.message, true);
        }
    }
);


uploadForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const fileInput =
            document.getElementById("document-file");

        if (!fileInput.files.length) {
            showMessage(
                "Please select a document.",
                true
            );

            return;
        }

        try {
            await uploadDocument(
                fileInput.files[0]
            );

            uploadForm.reset();
        } catch (error) {
            showMessage(error.message, true);
        }
    }
);


logoutButton.addEventListener(
    "click",
    () => {
        logout();
        showMessage("Logged out successfully.");
    }
);


refreshButton.addEventListener(
    "click",
    loadDocuments
);


if (token) {
    loadCurrentUser();
}