let cachedMatrixData = { compound: [], harvest: [] };
let activePhase = "compound";

document.addEventListener("DOMContentLoaded", () => {
    initThemeEngine(); 
    initPhaseEngine();
    fetchAutomatedDataStream();
});

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
}

function applyTheme(theme) {
    if (theme === "system") {
        const isSystemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        document.documentElement.setAttribute("data-theme", isSystemDark ? "dark" : "light");
    } else {
        document.documentElement.setAttribute("data-theme", theme);
    }
}

function initPhaseEngine() {
    const btnCompound = document.getElementById("btn-compound");
    const btnHarvest = document.getElementById("btn-harvest");
    
    if (!btnCompound || !btnHarvest) return;

    btnCompound.addEventListener("click", () => {
        activePhase = "compound";
        btnCompound.classList.add("active-phase-btn");
        btnHarvest.classList.remove("active-phase-btn");
        renderMatrixTable(cachedMatrixData.compound);
    });

    btnHarvest.addEventListener("click", () => {
        activePhase = "harvest";
        btnHarvest.classList.add("active-phase-btn");
        btnCompound.classList.remove("active-phase-btn");
        renderMatrixTable(cachedMatrixData.harvest);
    });
}

async function fetchAutomatedDataStream() {
    try {
        const response = await fetch(`./top20.json?nocache=${new Date().getTime()}`);
        if (!response.ok) throw new Error("Data stream baseline unreachable.");
        
        cachedMatrixData = await response.json();
        renderMatrixTable(cachedMatrixData[activePhase]);
    } catch (error) {
        console.error("Matrix stream sync sequence failure:", error.message);
    }
}

function renderMatrixTable(assets) {
    const targetContainer = document.getElementById('matrix-table-body');
    if (!targetContainer || !assets || assets.length === 0) {
        targetContainer.innerHTML = `<tr><td colspan="9" class="px-4 py-3 text-center text-gray-400">No assets currently meet the matching matrix limits for this phase.</td></tr>`;
        return;
    }
    
    let htmlContent = '';
    assets.forEach((asset, index) => {
        htmlContent += `
            <tr class="hover:bg-gray-50 border-b border-gray-100 transition-colors">
                <td class="px-4 py-3 font-bold text-gray-900">#${index + 1} - ${asset.ticker}</td>
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
}
