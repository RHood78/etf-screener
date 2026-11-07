/**
 * Quantum Dividend ETF Asset Screener - Core Application Script
 * Updated to support dynamic Compound vs. Harvest Phase switching
 */

// Global state to store the fetched datasets locally
let cachedMatrixData = { compound: [], harvest: [] };
let activePhase = "compound";

// --- 1. INITIALIZATION LIFECYCLE ---
document.addEventListener("DOMContentLoaded", () => {
    initThemeEngine(); 
    initPhaseEngine();
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
 * --- 2. PHASE ENGINE SWAP CONTROLLER ---
 */
function initPhaseEngine() {
    const btnCompound = document.getElementById("btn-compound");
    const btnHarvest = document.getElementById("btn-harvest");
    
    if (!btnCompound || !btnHarvest) return;

    btnCompound.addEventListener("click", () => {
        if (activePhase === "compound") return;
        activePhase = "compound";
        
        // Toggle visual UI button states
        btnCompound.classList.add("active-phase-btn");
        btnHarvest.classList.remove("active-phase-btn");
        
        // Render the filtered subset instantly
        renderMatrixTable(cachedMatrixData.compound);
    });

    btnHarvest.addEventListener("click", () => {
        if (activePhase === "harvest") return;
        activePhase = "harvest";
        
        // Toggle visual UI button states
        btnHarvest.classList.add("active-phase-btn");
        btnCompound.classList.remove("active-phase-btn");
        
        // Render the filtered subset instantly
        renderMatrixTable(cachedMatrixData.harvest);
    });
}

/**
 * --- 3. DUAL-STREAM JSON DATALAYER CONSUMER ---
 */
async function fetchAutomatedDataStream() {
    console.log("Initializing dual-phase matrix stream sync...");
    try {
        const response = await fetch(`./top20.json?nocache=${new Date().getTime()}`);
        
        if (!response.ok) {
            throw new Error(`Data store asset unreachable (Status: ${response.status})`);
        }
        
        // Save the structure containing both 'compound' and 'harvest' arrays
        cachedMatrixData = await response.json();
        
        // Initial render based on default phase choice
        renderMatrixTable(cachedMatrixData[activePhase]);
        
    } catch (error) {
        console.error("⚠️ Local Matrix Read Failure:", error.message);
    }
}

/**
 * --- 4. DOM RENDERING SEQUENCE ---
 */
function renderMatrixTable(assets) {
    const targetContainer = document.getElementById('matrix-table-body');
    if (!targetContainer || !assets) return;
    
    let htmlContent = '';
    
    assets.forEach((asset, index) => {
        const displayTicker = Array.isArray(asset.ticker) ? asset.ticker : asset.ticker;
        
        htmlContent += `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-800 border-b border-gray-100 dark:border-gray-700 transition-colors">
                <td class="px-4 py-3 font-bold text-gray-900 dark:text-gray-100">#${index + 1} - ${displayTicker}</td>
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
    console.log(`Matrix table updated complete for phase: ${activePhase}`);
}
