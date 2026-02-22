// ==========================================
// GLOBAL STATE
// ==========================================

let proposedData = null;
let currentStructure = {};
let proposedDiffMap = {};   // 🔥 ahora es MAPA


// ==========================================
// LOAD SYSTEM STATUS
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
                renderRawFile(screen, file);
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
        proposedDiffMap = data.diff || {};   // 🔥 ahora mapa

        renderProposed();
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

    if (!proposedData)
        return;

    const hasChanges =
        Array.isArray(proposedData.changes) &&
        proposedData.changes.length > 0;

    const hasFeatures =
        Array.isArray(proposedData.features) &&
        proposedData.features.length > 0;

    if (!hasChanges && !hasFeatures)
        return;

    showLoader();

    try {

        await fetch("/apply-proposed", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(proposedData)
        });

        proposedData = null;
        proposedDiffMap = {};

        updateActionButtons();
        await loadCurrentFeatures();

        document.getElementById("proposedFiles").innerHTML = "";
        document.getElementById("diffViewer").innerHTML = "";

    } catch (error) {
        alert("Error applying changes.");
        console.error(error);
    }

    hideLoader();
}


// ==========================================
// RENDER PROPOSED FILE LIST
// ==========================================

function renderProposed() {

    const container = document.getElementById("proposedFiles");
    container.innerHTML = "";

    if (!proposedDiffMap || Object.keys(proposedDiffMap).length === 0) {
        container.innerHTML = "<p>No changes proposed.</p>";
        return;
    }

    Object.keys(proposedDiffMap).forEach(fileKey => {

        const block = document.createElement("div");
        block.className = "file-item";
        block.innerHTML = `<strong>${fileKey}</strong>`;

        block.onclick = () => {
            renderFileDiff(fileKey);
        };

        container.appendChild(block);
    });
}


// ==========================================
// RENDER FILE DIFF (REAL GIT STYLE)
// ==========================================

function renderFileDiff(fileKey) {

    const viewer = document.getElementById("diffViewer");
    viewer.innerHTML = "";

    const diffLines = proposedDiffMap[fileKey];

    diffLines.forEach(line => {

        let className = "diff-unchanged";

        if (line.startsWith("+") && !line.startsWith("+++"))
            className = "diff-added";
        else if (line.startsWith("-") && !line.startsWith("---"))
            className = "diff-removed";

        viewer.innerHTML +=
            `<div class="diff-line ${className}">${escapeHtml(line)}</div>`;
    });
}


// ==========================================
// RENDER RAW FILE
// ==========================================

function renderRawFile(screen, file) {

    const viewer = document.getElementById("diffViewer");
    viewer.innerHTML = "";

    const rawContent = currentStructure[screen][file];

    viewer.innerHTML = rawContent
        .split("\n")
        .map(line =>
            `<div class="diff-line diff-unchanged">${escapeHtml(line)}</div>`
        ).join("");
}


// ==========================================
// BUTTON STATE
// ==========================================

function updateActionButtons() {

    const applyBtn = document.getElementById("applyButton");
    if (!applyBtn) return;

    const hasChanges =
        proposedData &&
        Array.isArray(proposedData.changes) &&
        proposedData.changes.length > 0;

    const hasFeatures =
        proposedData &&
        Array.isArray(proposedData.features) &&
        proposedData.features.length > 0;

    if (hasChanges || hasFeatures) {
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
// ANALYZE USER STORY
// ==========================================

async function analyzeStory() {

    const input = document.getElementById("analyzeInput");
    const output = document.getElementById("analyzeOutput");

    const story = input.value.trim();

    if (!story) {
        alert("Please enter a user story.");
        return;
    }

    output.value = "Analyzing...";

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title: "User Story",
                description: story
            })
        });

        const data = await response.json();

        output.value =
            `Summary:\n${data.summary}\n\n` +
            `Risk Level:\n${data.risk_level}\n\n` +

            `Missing Definitions:\n` +
            data.missing_definitions.map(i => `- ${i}`).join("\n") +
            `\n\n` +

            `Proposed Acceptance Criteria:\n` +
            data.acceptance_criteria_proposed.map(i => `- ${i}`).join("\n") +
            `\n\n` +

            `Edge Cases:\n` +
            data.edge_cases.map(i => `- ${i}`).join("\n") +
            `\n\n` +

            `Automation Notes:\n${data.automation_notes}`;

    } catch (error) {
        output.value = "Error during analysis.";
        console.error(error);
    }
}

// ==========================================
// INIT
// ==========================================

document.addEventListener("DOMContentLoaded", async () => {

    proposedData = null;
    proposedDiffMap = {};

    updateActionButtons();
    hideLoader();

    await loadSystemStatus();
    await loadCurrentFeatures();

    document.getElementById("diffViewer").innerHTML = "";
});