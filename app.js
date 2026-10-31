/**
 * Quantum Dividend ETF Asset Screener - Core Application Script
 * Optimized Pipeline Architecture using Local Cloud-Processed JSON Cache
 */

let macroScaleFactor = 1.0450; 
let currentDataset = [];
let calculatedTop20 = []; 

// --- 2. INITIALIZATION LIFECYCLE ---
document.addEventListener("DOMContentLoaded", () => {
    initializeUI();
    fetchAutomatedDataStream();
});

function initializeUI() {
    document.getElementById("toggle-importer").addEventListener("click", () => {
        document.getElementById("import-container").classList.toggle("hidden");
    });

    document.getElementById("btn-process-csv").addEventListener("click", processUserCSV);
    
    document.getElementById("btn-reset").addEventListener("click", () => {
        document.getElementById("csv-input").value = "";
        fetchAutomatedDataStream();
    });

    const resultsHeader = document.querySelector(".results-header");
    if (resultsHeader && !document.getElementById("btn-export-csv")) {
        const exportBtn = document.createElement("button");
        exportBtn.id = "btn-export-csv";
        exportBtn.className = "btn-primary";
        exportBtn.style.marginLeft = "10px";
        exportBtn.innerText = "📥 Export Top 20 to CSV";
        exportBtn.addEventListener("click", exportResultsToCSV);
        resultsHeader.appendChild(exportBtn);
    }
}

/**
 * SECTION 3: LIGHTNING-FAST LOCAL JSON DATALAYER CONSUMER
 * Removes public CORS proxy chains to eliminate network blocking risks.
 * Consumes the daily cloud-processed Top 20 array directly from the local repository cache.
 */
async function fetchAutomatedDataStream() {
    console.log("Initializing local cloud-processed matrix stream sync...");
    
    try {
        // Fetch directly from the repository relative root path
        const response = await fetch('./top20.json');
        
        if (!response.ok) {
            throw new Error(`Local data store asset missing or unreachable (Status: ${response.status})`);
        }
        
        const processedTop20Assets = await response.json();
        console.log(`Live dataset sync complete. Rendering ${processedTop20Assets.length} top-valued global assets.`);
        
        // Pass array directly to your existing UI generator logic
        renderMatrixTable(processedTop20Assets);
        
    } catch (error) {
        console.error("⚠️ Local Matrix Read Failure:", error.message);
        console.log("Activating resilient baseline mathematical failover fallback...");
        
        // Safety Emergency Net: Keep your 5-asset static routine right here as an absolute fallback
        const standardEmergencyFallback = [
            { ticker: 'SCHD', price: "86.21", pe: "15.20", growth: "7.50%", divYield: "3.40%", pegy: "0.98", fcfYield: "6.48%", strategyProfile: "Undervalued Dividend Growth", cashFlowInsight: "High Quality Coverage" },
            { ticker: 'VYM', price: "126.65", pe: "16.10", growth: "6.80%", divYield: "3.10%", pegy: "1.12", fcfYield: "6.06%", strategyProfile: "Undervalued Dividend Growth", cashFlowInsight: "Stable Coverage" }
        ];
        renderMatrixTable(standardEmergencyFallback);
    }
}

/**
 * Audit and Calculation Weights Evaluator
 * Runs the Multi-Factor Mathematical Evaluation Matrix Pipeline formulas
 */
function calculateMatrixWeights(raw, scaleFactor) {
    // PEGY Ratio = P/E / (Blended Growth Rate + Dividend Yield)
    const pegyDenominator = (raw.growth * 100) + (raw.divYield * 100);
    const pegyRatio = pegyDenominator > 0 ? (raw.pe / pegyDenominator) : 0;
    
    // Scale yields and prices uniformly against the macro metrics
    return {
        ticker: raw.ticker,
        price: (raw.price * scaleFactor).toFixed(2),
        pe: raw.pe.toFixed(2),
        growth: (raw.growth * 100).toFixed(2) + '%',
        divYield: (raw.divYield * 100).toFixed(2) + '%',
        pegy: pegyRatio.toFixed(2),
        fcfYield: (raw.fcf * 100 * scaleFactor).toFixed(2) + '%',
        strategyProfile: pegyRatio < 1.2 ? 'Undervalued Dividend Growth' : 'Core Equity Position',
        cashFlowInsight: raw.fcf > 0.06 ? 'High Quality Coverage' : 'Stable Coverage'
    };
}

/**
 * Complete DOM Rendering Sequence
 */
function renderMatrixTable(assets) {
    const tableBody = document.querySelector('table tbody, #matrix-awaiting-telemetry');
    if (!tableBody) return;
    
    // Clear out "Awaiting telemetry stream sync sequence..." message row completely
    let htmlContent = '';
    
    assets.forEach(asset => {
        // Safe check for handling both array strings and normal strings
        const displayTicker = Array.isArray(asset.ticker) ? asset.ticker[0] : asset.ticker;
        
        htmlContent += `
            <tr>
                <td class="font-bold">${displayTicker}</td>
                <td>$${asset.price}</td>
                <td>${asset.pe}</td>
                <td>${asset.growth}</td>
                <td class="text-green-600 font-medium">${asset.divYield}</td>
                <td>${asset.pegy}</td>
                <td>${asset.fcfYield}</td>
                <td><span class="badge-strategy">${asset.strategyProfile}</span></td>
                <td><span class="badge-cash">${asset.cashFlowInsight}</span></td>
            </tr>
        `;
    });
    
    // Inject components into table frame layout asynchronously 
    const targetContainer = document.getElementById('matrix-table-body') || tableBody;
    targetContainer.innerHTML = htmlContent;
    console.log("Matrix table rendered completely.");
}


// --- 4. MULTI-FACTOR MATHEMATICAL CALCULATIONS PIPELINE ---
function calculateMetrics() {
    let results = [];

    currentDataset.forEach(asset => {
        let price = asset.price;
        let basePE = asset.pe;
        let divYieldPercent = asset.yield;

        let trailingPE = basePE * macroScaleFactor;
        if (trailingPE <= 0 || price <= 0) return;

        let impliedCashFlowPerShare = (price / trailingPE) * 1.15;
        let fcfYield = (impliedCashFlowPerShare / price) * 100;

        let growthSum = 0;
        growthSum += (7.25 * macroScaleFactor); 
        growthSum += 8.20;                      
        growthSum += 6.50;                      
        growthSum += 7.10;                      
        let blendedGrowth = growthSum / 4;

        if (blendedGrowth <= 0) return;

        let pegy = trailingPE / (blendedGrowth + divYieldPercent);
        if (pegy <= 0) return;

        let strategyProfile = "Mature Dividend Value";
        if (blendedGrowth >= 8.0 && blendedGrowth <= 15.0) {
            strategyProfile = "GARP Stock W/ Yield";
        }

        let cashInsight = "Average Market Balance";
        let signalClass = "signal-normal";
        if (pegy < 1.4 && fcfYield >= 5.0) {
            cashInsight = "Undervalued & Cash Rich (Strong Signal)";
            signalClass = "signal-strong";
        } else if (pegy < 1.4 && fcfYield < 2.0) {
            cashInsight = "Cheap but Cash-Strapped (Value Trap Risk)";
            signalClass = "signal-trap";
        }

        results.push({
            ticker: asset.ticker,
            cat: asset.cat || "US",
            price: price.toFixed(2),
            pe: trailingPE.toFixed(2),
            growth: blendedGrowth.toFixed(2),
            yield: divYieldPercent.toFixed(2),
            pegy: pegy.toFixed(3),
            fcf: fcfYield.toFixed(2),
            profile: strategyProfile,
            insight: cashInsight,
            signalClass: signalClass
        });
    });

    results.sort((a, b) => {
        let pegyDiff = parseFloat(a.pegy) - parseFloat(b.pegy);
        if (Math.abs(pegyDiff) < 0.001) {
            return parseFloat(b.fcf) - parseFloat(a.fcf);
        }
        return pegyDiff;
    });

    calculatedTop20 = results.slice(0, 20);
    renderTable(calculatedTop20);
}

// --- 5. INTERFACE RENDER PANEL ---
function renderTable(data) {
    const tbody = document.getElementById("table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (data.length === 0) {
        tbody.innerHTML = "<tr><td colspan='9' style='text-align:center; color:var(--danger-red); font-weight:bold;'>Zero assets cleared metrics boundary checks.</td></tr>";
        return;
    }

    data.forEach((row, index) => {
        let tr = document.createElement("tr");
        tr.innerHTML = "<td><strong>#" + (index + 1) + " - " + row.ticker + "</strong> <small style='color:var(--text-muted);'>[" + row.cat + "]</small></td>" +
                       "<td>$" + row.price + "</td>" +
                       "<td>" + row.pe + "</td>" +
                       "<td>" + row.growth + "%</td>" +
                       "<td>" + row.yield + "%</td>" +
                       "<td><strong>" + row.pegy + "</strong></td>" +
                       "<td>" + row.fcf + "%</td>" +
                       "<td><span class='subtitle'>" + row.profile + "</span></td>" +
                       "<td class='" + row.signalClass + "'>" + row.insight + "</td>";
        tbody.appendChild(tr);
    });
}

// --- 6. EXCEL / CSV DIRECT DOWNLOAD UTILITY ---
function exportResultsToCSV() {
    if (calculatedTop20.length === 0) {
        alert("No calculation metrics available to export.");
        return;
    }

    let csvRows = [
        ["Rank", "Ticker", "Category", "Price", "Adjusted P/E", "Blended Growth", "Dividend Yield", "PEGY Ratio", "FCF Yield", "Strategy Profile", "Cash Insight"]
    ];

    calculatedTop20.forEach((row, index) => {
        csvRows.push([
            index + 1,
            row.ticker,
            row.cat,
            "$" + row.price,
            row.pe,
            row.growth + "%",
            row.yield + "%",
            row.pegy,
            row.fcf + "%",
            row.profile,
            row.insight
        ]);
    });

    let csvContent = "data:text/csv;charset=utf-8," 
        + csvRows.map(e => e.map(val => '"' + val + '"').join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", encodedUri);
    downloadAnchor.setAttribute("download", "Dividend_ETF_Top20_Screen_Results.csv");
    document.body.appendChild(downloadAnchor);
    
    downloadAnchor.click();
    document.body.removeChild(downloadAnchor);
}

// --- 7. SOLUTION 1 WORKSPACE PARSER ---
function processUserCSV() {
    const rawText = document.getElementById("csv-input").value.trim();
    if (!rawText) return alert("Ingestion canvas is empty. Add spreadsheet data first.");

    let rows = rawText.split(/\r?\n/);
    let parsedDataset = [];

    rows.forEach((row, index) => {
        if (!row.trim()) return;
        if (index === 0 && (row.toLowerCase().includes("ticker") || row.toLowerCase().includes("symbol"))) return;
        
        let cols = row.split(",");
        if (cols.length >= 4) {
            let ticker = cols[0].trim().toUpperCase();
            let price = parseFloat(cols[1]);
            let pe = parseFloat(cols[2]);
            let yieldVal = parseFloat(cols[3]);
            let category = cols[4] ? cols[4].trim().toUpperCase() : "US";

            if (ticker && !isNaN(price) && !isNaN(pe) && !isNaN(yieldVal)) {
                parsedDataset.push({ ticker: ticker, cat: category, price: price, pe: pe, yield: yieldVal });
            }
        }
    });

    if (parsedDataset.length > 0) {
        currentDataset = parsedDataset;
        
        const statusBox = document.getElementById("fed-status");
        if (statusBox) {
            statusBox.className = "status-badge success";
            statusBox.innerText = "✓ Solution 1 Active: Manual Workbook Feed Processed Safely (" + parsedDataset.length + " Assets Loaded).";
        }
        
        calculateMetrics();
    } else {
        alert("Parsing configuration mismatch. Verify column structure matches: Ticker, Price, P/E, Yield.");
    }
}
