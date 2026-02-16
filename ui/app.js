// ==========================================
// GLOBAL STATE
// ==========================================

let proposedData = null;
let currentStructure = {};
let systemStatus = null;

async function loadSystemStatus() {

    const res = await fetch("/system-status");
    const data = await res.json();

    // API status
    const apiStatus = document.getElementById("apiStatus");
    if (data.api_configured) {
        apiStatus.textContent = "API Key Configured";
        apiStatus.style.color = "green";
    } else {
        apiStatus.textContent = "No API Key";
        apiStatus.style.color = "red";
    }

    // Directory field
    const dirInput = document.getElementById("featuresDirInput");
    dirInput.value = data.features_directory;
}



// ==========================================
// API KEY MANAGEMENT
// ==========================================

async function checkApiKey() {
    const res = await fetch("/check-api-key");
    const data = await res.json();

    const status = document.getElementById("apiStatus");

    if (data.configured) {
        status.textContent = "API Key Configured";
        status.style.color = "green";
    } else {
        status.textContent = "No API Key";
        status.style.color = "red";
    }
}

async function saveApiKey() {

    const key = document.getElementById("apiKeyInput").value;

    const res = await fetch("/set-api-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key })
    });

    if (res.status === 200) {
        alert("API Key saved");
        checkApiKey();
    } else {
        alert("Invalid API Key");
    }
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
                document.getElementById("diffViewer").innerHTML =
                    data[screen][file]
                        .split("\n")
                        .map(line =>
                            `<div class="diff-line diff-unchanged">${escapeHtml(line)}</div>`
                        ).join("");
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
        
        renderProposed(proposedData);
        updateActionButtons()

        document.getElementById("applyButton").disabled = false;
        document.getElementById("downloadButton").disabled = false;


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

    if (!proposedData) return;

    showLoader();

    try {
        await fetch("/apply-proposed", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(proposedData)
        });

        proposedData = null;
        updateActionButtons();

        document.getElementById("applyButton").disabled = true;
        document.getElementById("downloadButton").disabled = true;

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

    if (!data || !data.features) return;

    data.features.forEach(feature => {

        const screen = feature.screen_name || "General";
        const fileName = feature.feature_name + ".feature";

        // Add screen header once
        if (!container.querySelector(`[data-screen="${screen}"]`)) {
            const screenTitle = document.createElement("div");
            screenTitle.innerHTML = `<strong>${screen}</strong>`;
            screenTitle.setAttribute("data-screen", screen);
            container.appendChild(screenTitle);
        }

        const fileItem = document.createElement("div");

        let isNew = true;

        if (currentStructure[screen] &&
            currentStructure[screen][fileName]) {
            isNew = false;
        }

        fileItem.className = isNew
            ? "file-item diff-added"
            : "file-item";

        fileItem.innerText = fileName;

        fileItem.onclick = () => {

            const newContent = buildGherkinFromFeature(feature);

            let oldContent = "";

            if (currentStructure[screen] &&
                currentStructure[screen][fileName]) {
                oldContent = currentStructure[screen][fileName];
            }

            if (!oldContent) {

                document.getElementById("diffViewer").innerHTML =
                    newContent.split("\n")
                        .map(line =>
                            `<div class="diff-line diff-added">+ ${escapeHtml(line)}</div>`
                        ).join("");

                return;
            }

            const diffHtml = generateDiff(oldContent, newContent);
            document.getElementById("diffViewer").innerHTML = diffHtml;
        };

        container.appendChild(fileItem);
    });
}

// ==========================================
// BUILD GHERKIN FROM FEATURE
// ==========================================

function buildGherkinFromFeature(feature) {

    let content = `Feature: ${feature.feature_name}\n\n`;

    feature.scenarios.forEach(scenario => {

        content += `  Scenario: ${scenario.name}\n`;

        scenario.steps.forEach(step => {
            content += `    ${step}\n`;
        });

        content += "\n";
    });

    return content;
}

// ==========================================
// DIFF ENGINE
// ==========================================

function generateDiff(oldText, newText) {

    const oldLines = oldText.split("\n");
    const newLines = newText.split("\n");

    const maxLength = Math.max(oldLines.length, newLines.length);
    let html = "";

    for (let i = 0; i < maxLength; i++) {

        const oldLine = oldLines[i] || "";
        const newLine = newLines[i] || "";

        if (oldLine === newLine) {
            html += `<div class="diff-line diff-unchanged">${escapeHtml(newLine)}</div>`;
        }
        else {
            if (oldLine) {
                html += `<div class="diff-line diff-removed">- ${escapeHtml(oldLine)}</div>`;
            }
            if (newLine) {
                html += `<div class="diff-line diff-added">+ ${escapeHtml(newLine)}</div>`;
            }
        }
    }

    return html;
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

async function downloadZip() {

    if (!proposedData) return;

    const response = await fetch("/download-proposed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(proposedData)
    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "proposed_tests.zip";
    a.click();
}

function updateActionButtons() {

    const applyBtn = document.getElementById("applyButton");
    const downloadBtn = document.getElementById("downloadButton");

    if (proposedData && proposedData.features && proposedData.features.length > 0) {

        applyBtn.disabled = false;
        downloadBtn.disabled = false;

        applyBtn.className = "button-success";
        downloadBtn.className = "button-success";

    } else {

        applyBtn.disabled = true;
        downloadBtn.disabled = true;

        applyBtn.className = "button-disabled";
        downloadBtn.className = "button-disabled";
    }
}

async function saveFeaturesDirectory() {

    const path = document.getElementById("featuresPathInput").value;

    const res = await fetch("/set-features-directory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ directory: path })
    });

    const data = await res.json();

    if (res.status === 200) {
        alert("Directory updated");
        loadCurrentFeatures();
    } else {
        alert(data.error);
    }
}

async function updateFeaturesDirectory() {

    const newDir = document.getElementById("featuresDirInput").value;

    const res = await fetch("/set-features-directory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ directory: newDir })
    });

    const data = await res.json();

    if (res.status !== 200) {
        alert(data.error || "Error updating directory");
        return;
    }

    alert("Directory updated");

    // Recargar estructura con el nuevo path
    await loadSystemStatus();
    await loadCurrentFeatures();

    // Limpiar proposed
    proposedData = null;
    updateActionButtons();
    document.getElementById("proposedFiles").innerHTML = "";
    document.getElementById("diffViewer").innerHTML = "";
}



// ==========================================
// INITIALIZE
// ==========================================

document.addEventListener("DOMContentLoaded", async () => {

    proposedData = null;
    currentData = null;
    currentStructure = {};

    updateActionButtons();
    hideLoader();

    await loadSystemStatus();     // carga API status + path
    await loadCurrentFeatures();  // carga árbol actual

    document.getElementById("diffViewer").innerHTML = "";
});


