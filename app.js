/**
 * Quantum Dividend ETF Asset Screener - Core Application Script
 * Dynamic Dual-Track Switcher Engine Edition
 */

let cachedMatrixData = { compound: [], harvest: [] };
let activePhase = "compound";

// --- 1. INITIALIZATION LIFECYCLE ---
document.addEventListener("DOMContentLoaded", () => {
    initThemeEngine(); 
    injectPhaseToggleInterface();
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
 * --- 2. DYNAMIC INTERFACE MANAGER ---
 * Injects non-breaking switch components dynamically to preserve clean styling setups
 */
function injectPhaseToggleInterface() {
    const scrollContainer = document.querySelector(".table-scroll-container");
    if (!scrollContainer) return;

    // Create the navigation selector frame matching native styling variables
    const toggleContainer = document.createElement("div");
    toggleContainer.style.cssText = "display: flex; gap: 10px; margin-bottom: 20px; align-items: center;";

    // Style and define compound tab button
    const btnCompound = document.createElement("button");
    btnCompound.id = "btn-compound";
    btnCompound.innerText = "🌱 Compound Phase (1.5% - 5.0%)";
    btnCompound.className = "btn-primary";
    btnCompound.style.cssText = "cursor: pointer; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: 700; border: none; font-size: 0.85rem; transition: background 0.15s ease;";

    // Style and define harvest tab button
    const btnHarvest = document.createElement("button");
    btnHarvest.id = "btn-harvest";
    btnHarvest.innerText = "🌾 Harvest Phase (5.1% - 8.0%)";
    btnHarvest.className = "btn-primary";
    btnHarvest.style.cssText = "cursor: pointer; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: 700; border: none; font-size: 0.85rem; opacity: 0.5; background-color: #6e8c80; transition: background 0.15s ease;";

    toggleContainer.appendChild(btnCompound);
    toggleContainer.appendChild(btnHarvest);

    // Place the switcher directly right above your data grid table viewport
    scrollContainer.parentNode.insertBefore(toggleContainer, scrollContainer);

    // Interaction wiring layer
    btnCompound.addEventListener("click", () => {
        activePhase = "compound";
        btnCompound.style.opacity = "1";
        btnCompound.style.backgroundColor = "";
        btnHarvest.style.opacity = "0.5";
        btnHarvest.style.backgroundColor = "#6e8c80";
        renderMatrixTable(cachedMatrixData.compound);
    });

    btnHarvest.addEventListener("click", () => {
        activePhase = "harvest";
        btnHarvest.style.opacity = "1";
        btnHarvest.style.backgroundColor = "";
        btnCompound.style.opacity = "0.5";
        btnCompound.style.backgroundColor = "#6e8c80";
        renderMatrixTable(cachedMatrixData.harvest);
    });
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
        
        cachedMatrixData = await response.json();
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
    if (!targetContainer) return;
    
    if (!assets || assets.length === 0) {
        targetContainer.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 2rem; color: var(--text-muted);">No matching tracking tokens found for this matrix setup.</td></tr>`;
        return;
    }
    
    let htmlContent = '';
    
    assets.forEach((asset, index) => {
        const displayTicker = Array.isArray(asset.ticker) ? asset.ticker : asset.ticker;
        
        htmlContent += `
            <tr class="hover:bg-gray-50 border-b border-gray-100 transition-colors">
                <td class="px-4 py-3 font-bold">#\${index + 1} - \${displayTicker}</td>
                <td class="px-4 py-3">$\${asset.price}</td>
                <td class="px-4 py-3">\${asset.pe}</td>
                <td class="px-4 py-3">\${asset.growth}</td>
                <td class="px-4 py-3 text-green-600 font-medium">\${asset.divYield}</td>
                <td class="px-4 py-3 font-medium">\${asset.pegy}</td>
                <td class="px-4 py-3">\${asset.fcfYield}</td>
                <td class="px-4 py-3"><span class="badge-strategy">\${asset.strategyProfile}</span></td>
                <td class="px-4 py-3"><span class="badge-cash">\${asset.cashFlowInsight}</span></td>
            </tr>
        `;
    });
    
    targetContainer.innerHTML = htmlContent;
    console.log("Matrix table rendered completely.");
}
