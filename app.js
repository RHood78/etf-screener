/**
 * Quantum Dividend ETF Asset Screener - Core Application Script
 * Consumes the daily cloud-processed Growth & Harvest Top 20 buckets.
 */

let matrixDataStore = {
    growth: [],
    harvest: []
};
let activeBucket = "growth";

// --- 1. INITIALIZATION LIFECYCLE ---
document.addEventListener("DOMContentLoaded", () => {
    initThemeEngine();
    initBucketButtons();
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
 * --- 2. STRATEGY NAVIGATION BUTTONS ---
 * Wired directly to #filter-growth, #filter-harvest, and #matrix-portfolio-title
 */
function initBucketButtons() {
    const growthBtn = document.getElementById("filter-growth");
    const harvestBtn = document.getElementById("filter-harvest");

    if (growthBtn) {
        growthBtn.addEventListener("click", () => switchBucket("growth"));
    }
    if (harvestBtn) {
        harvestBtn.addEventListener("click", () => switchBucket("harvest"));
    }
}

function switchBucket(bucketName) {
    activeBucket = bucketName;

    const growthBtn = document.getElementById("filter-growth");
    const harvestBtn = document.getElementById("filter-harvest");
    const portfolioTitle = document.getElementById("matrix-portfolio-title");

    // Toggle active button styling
    if (growthBtn && harvestBtn) {
        growthBtn.classList.toggle("active", bucketName === "growth");
        harvestBtn.classList.toggle("active", bucketName === "harvest");
    }

    // Update section heading to match active portfolio
    if (portfolioTitle) {
        const label = bucketName === "growth" ? "Growth" : "Harvest";
        portfolioTitle.textContent = `Top 20 Filtered Investment Assets (${label})`;
    }

    renderMatrixTable(matrixDataStore[activeBucket] || []);
}

/**
 * --- 3. FAST LOCAL JSON DATALAYER CONSUMER ---
 */
async function fetchAutomatedDataStream() {
    console.log("Initializing local cloud-processed matrix stream sync...");
    try {
        const response = await fetch(`./top20.json?nocache=${new Date().getTime()}`);

        if (!response.ok) {
            throw new Error(`Data store asset unreachable (Status: ${response.status})`);
        }

        const payload = await response.json();

        // Support both { growth: [...], harvest: [...] } and legacy flat arrays
        if (Array.isArray(payload)) {
            matrixDataStore.growth = payload;
            matrixDataStore.harvest = [];
        } else {
            matrixDataStore.growth = payload.growth || [];
            matrixDataStore.harvest = payload.harvest || [];
        }

        renderMatrixTable(matrixDataStore[activeBucket]);

    } catch (error) {
        console.error("⚠️ Local Matrix Read Failure:", error.message);
    }
}

/**
 * --- 4. DOM RENDERING SEQUENCE ---
 */
function renderMatrixTable(assets) {
    const targetContainer = document.getElementById("matrix-table-body");
    if (!targetContainer) return;

    if (!assets || assets.length === 0) {
        targetContainer.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 30px;">
                    No assets currently qualify for the ${activeBucket.toUpperCase()} portfolio.
                </td>
            </tr>
        `;
        return;
    }

    let htmlContent = "";

    assets.forEach((asset, index) => {
        const displayTicker = Array.isArray(asset.ticker) ? asset.ticker[0] : asset.ticker;

        // Prevent double '%%' since Python already appends '%'
        const rawYield = String(asset.divYield || "");
        const divYield = rawYield ? (rawYield.endsWith("%") ? rawYield : `${rawYield}%`) : "N/A";

        const pe = asset.pe || "N/A";
        const growth = asset.growth || "N/A";
        const pegy = asset.pegy || "N/A";
        const fcfYield = asset.fcfYield || "N/A";
        const strategyProfile = asset.strategyProfile || "N/A";
        const cashFlowInsight = asset.cashFlowInsight || "N/A";

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
    console.log(`Matrix table rendered completely for [${activeBucket}].`);
}
