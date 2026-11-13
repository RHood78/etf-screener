/**
 * Quantum Dividend ETF Asset Screener - Core Application Script
 * Consumes the daily cloud-processed Top 20 array directly from the repository cache.
 */
// --- 1. INITIALIZATION LIFECYCLE ---
document.addEventListener("DOMContentLoaded", () => {
    initThemeEngine();
    fetchAutomatedDataStream();
});

/**
 * Theme Engine Orchestration Module
 */
function initThemeEngine() {
    const themeSelect = document.getElementById("theme-select");
    if (!themeSelect) return;
    const savedTheme = localStorage.getItem("screener-theme") || "system";
    themeSelect.value = savedTheme;
    applyTheme(savedTheme);
    themeSelect.addEventListener("change", (e) => {
        const chosenTheme = e.target.value;
        localStorage.setItem("screener-theme", chosenTheme);
        applyTheme(chosenTheme);
    });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
        if (themeSelect.value === "system") applyTheme("system");
    });
}

function applyTheme(theme) {
    if (theme === "system") {
        const isSystemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        document.documentElement.setAttribute("data-theme", isSystemDark ? "dark" : "light");
    } else {
        document.documentElement.setAttribute("data-theme", theme);
    }
}

/**
 * --- 2. FAST LOCAL JSON DATALAYER CONSUMER ---
 */
async function fetchAutomatedDataStream() {
    console.log("Initializing local cloud-processed matrix stream sync...");
    try {
        // Cache buster forces browser to always fetch fresh metrics without server edge throttling
        const response = await fetch(`./top20.json?nocache=${new Date().getTime()}`);

        if (!response.ok) {
            throw new Error(`Data store asset unreachable (Status: ${response.status})`);
        }

        const processedTop20Assets = await response.json();
        renderMatrixTable(processedTop20Assets);

    } catch (error) {
        console.error("⚠️ Local Matrix Read Failure:", error.message);
    }
}

/**
 * --- 3. DOM RENDERING SEQUENCE ---
 */
function renderMatrixTable(assets) {
    // FIXED: Maps directly to your live 'matrix-table-body' table container ID
    const targetContainer = document.getElementById('matrix-table-body');
    if (!targetContainer) return;

    let htmlContent = '';

    assets.forEach((asset, index) => {
        const displayTicker = Array.isArray(asset.ticker) ? asset.ticker : asset.ticker;

        // Validate and handle missing or invalid data
        const divYield = asset.divYield ? `${asset.divYield}%` : 'N/A';
        const pe = asset.pe || 'N/A';
        const growth = asset.growth || 'N/A';
        const pegy = asset.pegy || 'N/A';
        const fcfYield = asset.fcfYield || 'N/A';
        const strategyProfile = asset.strategyProfile || 'N/A';
        const cashFlowInsight = asset.cashFlowInsight || 'N/A';

        htmlContent += `
            <tr class="hover:bg-gray-50 border-b border-gray-100 transition-colors">
                <td class="px-4 py-3 font-bold text-gray-900">#${index + 1} - ${displayTicker}</td>
                <td class="px-4 py-3">$${asset.price}</td>
                <td class="px-4 py-3">${pe}</td>
                <td class="px-4 py-3">${growth}</td>
                <td class="px-4 py-3 text-green-600 font-medium">${divYield}</td>
                <td class="px-4 py-3 font-medium">${pegy}</td>
                <td class="px-4 py-3">${fcfYield}</td>
                <td class="px-4 py-3"><span class="badge-strategy">${strategyProfile}</span></td>
                <td class="px-4 py-3"><span class="badge-cash">${cashFlowInsight}</span></td>
            </tr>
        `;
    });

    targetContainer.innerHTML = htmlContent;
    console.log("Matrix table rendered completely.");
}
