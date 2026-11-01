/**
 * Quantum Dividend ETF Asset Screener - Pure Datalayer Viewer
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
    const targetContainer = document.getElementById('matrix-table-body');
    if (!targetContainer) return;
    
    let htmlContent = '';
    
    assets.forEach((asset, index) => {
        const displayTicker = Array.isArray(asset.ticker) ? asset.ticker[0] : asset.ticker;
        
        htmlContent += `
            <tr class="hover:bg-gray-50 border-b border-gray-100 transition-colors">
                <td class="px-4 py-3 font-bold text-gray-900">#${index + 1} - ${displayTicker}</td>
                <td class="px-4 py-3">$${asset.price}</td>
                <td class="px-4 py-3">${asset.pe}</td>
                <td class="px-4 py-3">${asset.growth}</td>
                <td class="px-4 py-3 text-green-600 font-medium">${asset.divYield}</td>
                <td class="px-4 py-3 font-medium">${asset.pegy}</td>
                <td class="px-4 py-3">${asset.fcfYield}</td>
                <td class="px-4 py-3"><span class="badge-strategy">${asset.strategyProfile}</span></td>
                <td class="px-4 py-3"><span class="badge-cash">${asset.cashFlowInsight}</span></td>
            </tr>
        `;
    });
    
    targetContainer.innerHTML = htmlContent;
    console.log("Matrix table rendered completely.");
}
