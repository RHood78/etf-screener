/**
 * Quantum Dividend ETF Asset Screener - Core Application Script
 * Consumes the daily cloud-processed Top 20 array directly from the repository cache.
 */

// Global state cache to hold the separate portfolio matrices
let cachedGrowthAssets = [];
let cachedHarvestAssets = [];
let activePortfolio = "growth"; // Defaults to tracking growth segments first

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
 * --- 2. FAST DUAL-KEY DATA CONSUMER ---
 */
async function fetchAutomatedDataStream() {
    console.log("Initializing split-key cloud matrix stream sync...");
    try {
        const response = await fetch(`./top20.json?nocache=${new Date().getTime()}`);
        
        if (!response.ok) {
            throw new Error(`Data store asset unreachable (Status: ${response.status})`);
        }
        
        const masterPayload = await response.json();
        
        // Explicitly ingest individual portfolio tracking buckets
        cachedGrowthAssets = masterPayload.growth || [];
        cachedHarvestAssets = masterPayload.harvest || [];
        
        // Render initial default view
        routeActivePortfolio();
        
    } catch (error) {
        console.error("⚠️ Local Matrix Read Failure:", error.message);
        const targetContainer = document.getElementById('matrix-table-body');
        if (targetContainer) {
            targetContainer.innerHTML = `<tr><td colspan="9" style="text-align: center; color: red; padding: 20px;">Failed to sync live matrix stream data.</td></tr>`;
        }
    }
}

/**
 * --- 3. DYNAMIC STRATEGY FILTRATION ROUTER ---
 */
function initFilterEngine() {
    const btnGrowth = document.getElementById("filter-growth");
    const btnHarvest = document.getElementById("filter-harvest");

    if (!btnGrowth || !btnHarvest) return;

    btnGrowth.addEventListener("click", () => {
        btnHarvest.classList.remove("active");
        btnGrowth.classList.add("active");
        activePortfolio = "growth";
        routeActivePortfolio();
    });

    btnHarvest.addEventListener("click", () => {
        btnGrowth.classList.remove("active");
        btnHarvest.classList.add("active");
        activePortfolio = "harvest";
        routeActivePortfolio();
    });
}

function routeActivePortfolio() {
    const portfolioTitle = document.getElementById("matrix-portfolio-title");
    
    if (activePortfolio === "growth") {
        if (portfolioTitle) portfolioTitle.innerText = "Top 20 Filtered Investment Assets (Growth)";
        renderMatrixTable(cachedGrowthAssets);
    } else {
        if (portfolioTitle) portfolioTitle.innerText = "Top 20 Filtered Investment Assets (Harvest)";
        renderMatrixTable(cachedHarvestAssets);
    }
}

/**
 * --- 4. DOM RENDERING SEQUENCE ---
 */
function renderMatrixTable(assets) {
    const targetContainer = document.getElementById('matrix-table-body');
    if (!targetContainer) return;
    
    if (assets.length === 0) {
        targetContainer.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 30px;">No investment assets found matching the active filtration criteria.</td></tr>`;
        return;
    }
    
    let htmlContent = '';
    
    assets.forEach((asset, index) => {
        const displayTicker = Array.isArray(asset.ticker) ? asset.ticker : asset.ticker;
        
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
    console.log(`Matrix table successfully updated for theme profile: ${activePortfolio}`);
}
