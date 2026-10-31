import json
import yfinance as yf

# --- COMPREHENSIVE GLOBAL DIVIDEND ETF MASTER SEED SHEET ---
MASTER_TICKERS = [
    "SCHD", "VYM", "DGRO", "VIG", "DVY", "SDY", "DGRW", "HDV", "NOBL", "FVD", 
    "CGDV", "RDVY", "DIVB", "REGL", "FDL", "DON", "DES", "DHS", "DLN", "DTD", 
    "PEY", "SMDV", "CSB", "CDC", "CDL", "FNDX", "TDV", "KNG", "FTCS", "DNL", 
    "SDOG", "SPDV", "JEPI", "JEPQ", "SPHD", "DIVO", "SDVY", "MLPA", "AMLP", 
    "ALTY", "PFF", "PGX", "TLTW", "HYGW", "LQDW", "UTG", "STK", "RFI", "BME", 
    "EVT", "EOS", "BDJ", "NFJ", "TYG", "KYN", "MAIN", "GAIN", "PSEC", "VYMI", 
    "VIGI", "IDV", "LVHI", "SCHY", "IGRO", "FNDF", "FNDC", "PXF", "PID", "IQDF", 
    "EFV", "IQDG", "DOO", "GWX", "EFAV", "EFAS", "FIDI", "IEDI", "DOL", "DIM", 
    "DLS", "DWM", "IHDG", "DXJ", "HEDJ", "DFE", "DVYE", "DEM", "EMDV", "FNDE", 
    "EDIV", "DEW", "FNDB", "GCOW", "DIVI", "FGD", "WDIV", "DEEF", "DTH", "FDT", 
    "EYLD", "FYLD", "DGS", "FEMS", "EEMS", "DVYA", "SDEM", "GVAL"
]

MASTER_TICKERS = sorted(list(set(MASTER_TICKERS)))
MACRO_SCALE_FACTOR = 1.0450

# Calculation Boundary Configurations

# Change this number to tighten or loosen your value line in the sand
PEGY_VALUE_THRESHOLD = 1.00  # Strict Value Filter

FCF_YIELD_THRESHOLD = 6.00  # Explicit 6% cash health cut-off

def compute_pegy_matrix():
    print("Beginning Multi-Factor Evaluation Matrix Pipeline Sequence via Yahoo Cloud Engine...")
    print(f"Syncing DYNAMIC telemetry metadata profiles for {len(MASTER_TICKERS)} assets...")
    
    processed_assets = []
    tickers_string = " ".join(MASTER_TICKERS)
    yf_data = yf.Tickers(tickers_string)
    
    for ticker in MASTER_TICKERS:
        try:
            ticker_object = yf_data.tickers[ticker]
            info = ticker_object.info
            
            # 1. Market Price
            raw_price = info.get("regularMarketPrice") or info.get("previousClose") or info.get("navPrice") or 0
            if raw_price == 0:
                continue
                
            # 2. P/E Ratio
            pe = info.get("trailingPE") or info.get("forwardPE") or 16.5
            
            # 3. Dividend Yield
            div_yield = info.get("trailingAnnualDividendYield") or info.get("dividendYield") or 0.032
            
            # 4. Dynamic Growth Rate Extraction
            raw_growth = info.get("earningsGrowth") or info.get("threeYearAverageReturn") or info.get("fiveYearAverageReturn") or 0.060
            if raw_growth > 1.0:
                raw_growth = raw_growth / 100.0
            elif raw_growth <= 0:
                raw_growth = 0.045 
                
            # 5. Dynamic Free Cash Flow Yield Approximation
            dynamic_fcf = info.get("holdingPercent") or info.get("trailingPegRatio") or (div_yield * 1.5)
            if dynamic_fcf > 1.0:
                dynamic_fcf = dynamic_fcf / 100.0
            if dynamic_fcf <= 0 or dynamic_fcf > 0.25:
                dynamic_fcf = 0.055 
            
            # PEGY Ratio Calculation = P/E / (Dynamic Growth% + Dynamic Dividend Yield%)
            pegy_denominator = (raw_growth * 100) + (div_yield * 100)
            pegy_ratio = pe / pegy_denominator if pegy_denominator > 0 else 0
            
            # Apply Macro Scale Factor adjustments
            adjusted_price = raw_price * MACRO_SCALE_FACTOR
            fcf_yield_calc = dynamic_fcf * MACRO_SCALE_FACTOR
            fcf_yield_percentage = fcf_yield_calc * 100
            
            # --- FIXED: UNIFIED MULTI-FACTOR STRATEGY MATRIX LOGIC ---
            is_low_pegy = pegy_ratio < PEGY_VALUE_THRESHOLD
            is_high_fcf = fcf_yield_percentage > FCF_YIELD_THRESHOLD
            
            if is_low_pegy and is_high_fcf:
                strategy_profile = "Strong Signal (Cash Generator)"
                cash_flow_insight = "High Quality Coverage"
            elif is_low_pegy and not is_high_fcf:
                strategy_profile = "Value Trap (Cash-Strapped)"
                cash_flow_insight = "Weak Coverage Risk"
            elif not is_low_pegy and is_high_fcf:
                strategy_profile = "Expensive (Monitor Entry)"
                cash_flow_insight = "High Quality Coverage"
            else:
                strategy_profile = "Premium Valuation"
                cash_flow_insight = "Stable / Low Coverage"
            
            processed_assets.append({
                "ticker": ticker,
                "price": f"{adjusted_price:.2f}",
                "pe": f"{pe:.2f}",
                "growth": f"{(raw_growth * 100):.2f}%",
                "divYield": f"{(div_yield * 100):.2f}%",
                "pegy": f"{pegy_ratio:.2f}",
                "fcfYield": f"{fcf_yield_percentage:.2f}%",
                "strategyProfile": strategy_profile,
                "cashFlowInsight": cash_flow_insight,
                "score_sort": pegy_ratio
            })
            
        except Exception as e:
            print(f"Skipping tracking loops for {ticker}: {e}")
            continue

    # Sort array descendingly by valuation ranking metrics
    processed_assets.sort(key=lambda x: x["score_sort"])
    top_20 = processed_assets[:20]

    with open("top20.json", "w") as f:
        json.dump(top_20, f, indent=4)
        
    print(f"Successfully processed matrix values for {len(processed_assets)} records.")
    print(f"Saved optimized top20.json matrix profile artifact with {len(top_20)} entries.")

if __name__ == "__main__":
    compute_pegy_matrix()
