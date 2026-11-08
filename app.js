/**
 * Quantum Dividend ETF Asset Screener - Core Application Script
 * Consumes the daily cloud-processed Top 20 array directly from the repository cache.
 */

// Global state cache to hold live data payload for instant script filtering
let cachedAssets = [];

// --- 1. INITIALIZATION LIFECYCLE ---
document.addEventListener("DOMContentLoaded", () => {
    initThemeEngine(); 
    fetchAutomatedDataStream();
    initFilterEngine();
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
        const response = await fetch(`./top20.json?nocache=${new Date().getTime()}`);
        
        if (!response.ok) {
            throw new Error(`Data store asset unreachable (Status: ${response.status})`);
        }
        
        cachedAssets = await response.json();
        renderMatrixTable(cachedAssets);
        
    } catch (error) {
        console.error("⚠️ Local Matrix Read Failure:", error.message);
        const targetContainer = document.getElementById('matrix-telemetry-body');
        if (targetContainer) {
            targetContainer.innerHTML = `<tr><td colspan="9" style="text-align: center; color: red; padding: 20px;">Failed to sync live matrix stream data.</td></tr>`;
        }
    }
}

/**
 * --- 3. DYNAMIC STRATEGY FILTRATION MODULE ---
 */
function initFilterEngine() {
    const btnAll = document.getElementById("filter-all");
    const btnGrowth = document.getElementById("filter-growth");
    const btnHarvest = document.getElementById("filter-harvest");

    if (!btnAll || !btnGrowth || !btnHarvest) return;

    const buttons = [btnAll, btnGrowth, btnHarvest];

    function updateActiveButtonState(activeBtn) {
        buttons.forEach(btn => btn.classList.remove("active"));
        activeBtn.classList.add("active");
    }

    btnAll.addEventListener("click", () => {
        updateActiveButtonState(btnAll);
        renderMatrixTable(cachedAssets);
    });

    btnGrowth.addEventListener("click", () => {
        updateActiveButtonState(btnGrowth);
        const growthFiltered = cachedAssets.filter(asset => {
            const yieldVal = parseFloat(asset.divYield.replace('%', ''));
            return yieldVal >= 1.5 && yieldVal <= 5.0;
        });
        renderMatrixTable(growthFiltered);
    });

    btnHarvest.addEventListener("click", () => {
        updateActiveButtonState(btnHarvest);
        const harvestFiltered = cachedAssets.filter(asset => {
            const yieldVal = parseFloat(asset.divYield.replace('%', ''));
            return yieldVal >= 5.1 && yieldVal <= 8.0;
        });
        renderMatrixTable(harvestFiltered);
    });
}

/**
 * --- 4. DOM RENDERING SEQUENCE ---
 */
function renderMatrixTable(assets) {
    const targetContainer = document.getElementById('matrix-telemetry-body');
    if (!targetContainer) return;
    
    if (assets.length === 0) {
        targetContainer.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 20px;">No investment assets match the active filtration window.</td></tr>`;
        return;
    }
    
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
