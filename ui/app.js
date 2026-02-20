// ==========================================
// GLOBAL STATE
// ==========================================

let proposedData = null;
let currentStructure = {};
let proposedDiff = [];
let proposedDiffMap = {}; // file -> diff lines


// ==========================================
// SYSTEM STATUS
// ==========================================

async function loadSystemStatus() {
    const res = await fetch("/system-status");
    const data = await res.json();

    const apiStatus = document.getElementById("apiStatus");

    if (data.api_configured) {
        apiStatus.textContent = "API Key Configured";
        apiStatus.style.color = "green";
    } else {
        apiStatus.textContent = "No API Key";
        apiStatus.style.color = "red";
    }

    document.getElementById("featuresDirInput").value =
        data.features_directory;
}


// ==========================================
// LOAD CURRENT FEATURES
// ==========================================

async function loadCurrentFeatures() {

    const response = await fetch("/test-structure");
    const data = await response.json();

    currentStructure = data;

    const container = document.getElementById("currentFiles");
    container.innerHTML = "";

    Object.keys(data).forEach(screen => {

        const screenTitle = document.createElement("div");
        screenTitle.innerHTML = `<strong>${screen}</strong>`;
        container.appendChild(screenTitle);

        Object.keys(data[screen]).forEach(file => {

            const fileItem = document.createElement("div");
            fileItem.className = "file-item";
            fileItem.innerText = file;

            fileItem.onclick = () => {
                renderFile(screen, file);
            };

            container.appendChild(fileItem);
        });
    });
}


// ==========================================
// GENERATE (DRY RUN)
// ==========================================

async function generate() {

    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a file first.");
        return;
    }

    showLoader();

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("/sync-tests?dry_run=true", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        proposedData = data.result;
        proposedDiff = data.diff || [];

        buildDiffMap();

        renderProposed(proposedData);
        updateActionButtons();

    } catch (error) {
        alert("Error generating features.");
        console.error(error);
    }

    hideLoader();
}


// ==========================================
// APPLY CHANGES
// ==========================================

async function applyChanges() {

    if (!proposedData || !proposedData.changes || proposedData.changes.length === 0)
        return;

    showLoader();

    try {

        await fetch("/apply-proposed", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(proposedData)
        });

        proposedData = null;
        proposedDiff = [];
        proposedDiffMap = {};

        updateActionButtons();

        await loadCurrentFeatures();

        document.getElementById("proposedFiles").innerHTML = "";
        document.getElementById("diffViewer").innerHTML = "";

    } catch (error) {
        alert("Error applying changes.");
    }

    hideLoader();
}


// ==========================================
// RENDER PROPOSED
// ==========================================

function renderProposed(data) {

    const container = document.getElementById("proposedFiles");
    container.innerHTML = "";

    if (!data || !data.changes || data.changes.length === 0) {
        container.innerHTML = "<p>No changes proposed.</p>";
        return;
    }

    data.changes.forEach(change => {

        const block = document.createElement("div");
        block.style.padding = "10px";
        block.style.marginBottom = "8px";
        block.style.background = "#f8f9fa";
        block.style.border = "1px solid #ddd";
        block.style.borderRadius = "6px";

        block.innerHTML = `
            <div><strong>${change.action}</strong></div>
            <div>${change.screen} → ${change.feature}</div>
            <div>${change.scenario || ""}</div>
        `;

        container.appendChild(block);
    });
}


// ==========================================
// DIFF PER FILE
// ==========================================

function buildDiffMap() {

    proposedDiffMap = {};

    if (!proposedDiff || proposedDiff.length === 0)
        return;

    let currentFile = null;

    proposedDiff.forEach(line => {

        if (line.startsWith("+++ ")) {
            currentFile = line.replace("+++ ", "").trim();
            proposedDiffMap[currentFile] = [];
            return;
        }

        if (!currentFile) return;

        proposedDiffMap[currentFile].push(line);
    });
}


function renderFile(screen, file) {

    const viewer = document.getElementById("diffViewer");
    viewer.innerHTML = "";

    const rawContent = currentStructure[screen][file];

    const fullPath = `${screen}/${file}`;

    // If no proposed changes → show normal
    if (!proposedData || !proposedData.changes || proposedData.changes.length === 0) {

        viewer.innerHTML = rawContent
            .split("\n")
            .map(line =>
                `<div class="diff-line diff-unchanged">${escapeHtml(line)}</div>`
            ).join("");

        return;
    }

    // If file has no diff → show normal
    if (!proposedDiffMap[fullPath]) {

        viewer.innerHTML = rawContent
            .split("\n")
            .map(line =>
                `<div class="diff-line diff-unchanged">${escapeHtml(line)}</div>`
            ).join("");

        return;
    }

    // Show Git style diff
    proposedDiffMap[fullPath].forEach(line => {

        let className = "diff-unchanged";

        if (line.startsWith("+") && !line.startsWith("+++")) {
            className = "diff-added";
        }
        else if (line.startsWith("-") && !line.startsWith("---")) {
            className = "diff-removed";
        }

        viewer.innerHTML +=
            `<div class="diff-line ${className}">${escapeHtml(line)}</div>`;
    });
}


// ==========================================
// BUTTON STATE
// ==========================================

function updateActionButtons() {

    const applyBtn = document.getElementById("applyButton");

    if (!applyBtn) return;   // 🔥 PROTECCIÓN CLAVE

    if (proposedData && proposedData.changes && proposedData.changes.length > 0) {

        applyBtn.disabled = false;
        applyBtn.className = "button-success";

    } else {

        applyBtn.disabled = true;
        applyBtn.className = "button-disabled";
    }
}


// ==========================================
// UTILITIES
// ==========================================

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function showLoader() {
    document.getElementById("loader").style.display = "inline";
}

function hideLoader() {
    document.getElementById("loader").style.display = "none";
}


// ==========================================
// INIT
// ==========================================

document.addEventListener("DOMContentLoaded", async () => {

    proposedData = null;
    proposedDiff = [];
    proposedDiffMap = {};

    updateActionButtons();
    hideLoader();

    await loadSystemStatus();
    await loadCurrentFeatures();

    document.getElementById("diffViewer").innerHTML = "";
});
