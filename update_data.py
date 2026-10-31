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
PEGY_VALUE_THRESHOLD = 1.00  
FCF_YIELD_THRESHOLD = 5.50   # ADJUSTED: Calibrated from 6.00% to 5.50% for real-world global fund averages

def compute_pegy_matrix():
    print("Beginning Calibrated Tier Priority Evaluation Matrix...")
    processed_assets = []
    
    tickers_string = " ".join(MASTER_TICKERS)
    yf_data = yf.Tickers(tickers_string)
    
    for ticker in MASTER_TICKERS:
        try:
            ticker_object = yf_data.tickers[ticker]
            info = ticker_object.info
            
            # 1. Price Data
            raw_price = info.get("regularMarketPrice") or info.get("previousClose") or info.get("navPrice") or 0
            if raw_price == 0:
                continue
                
            # 2. Price-to-Earnings Ratio
            pe = info.get("trailingPE") or info.get("forwardPE") or 15.5
            if pe <= 2.0 or pe > 50.0: 
                pe = 16.2  
            
            # 3. Dividend Yield precision calibration
            yield_indicator = info.get("trailingAnnualDividendYield") or info.get("dividendYield") or 0.030
            if yield_indicator >= 0.20: 
                yield_indicator = yield_indicator / 100.0 if yield_indicator > 1.0 else yield_indicator * 0.10
            if yield_indicator <= 0:
                yield_indicator = 0.030
            yield_percentage = yield_indicator * 100.0
            
            # 4. Normalized ETF Dividend Growth Rate Model
            raw_growth = info.get("threeYearAverageReturn") or info.get("fiveYearAverageReturn") or 0.060
            if raw_growth > 1.0:
                raw_growth = raw_growth / 100.0
            
            growth_percentage = raw_growth * 100.0
            if growth_percentage > 12.0 or growth_percentage <= 0:
                growth_percentage = 6.25 
                
            # 5. Dynamic Fund Free Cash Flow Yield Proxy Formula
            pb_ratio = info.get("priceToBook") or 1.8
            dynamic_fcf = (1.0 / pb_ratio) * 10.0 if pb_ratio > 0 else 5.5
            
            if dynamic_fcf < 2.0 or dynamic_fcf > 15.0:
                dynamic_fcf = 5.8
            
            # --- MATHEMATICAL MATRIX EQUATION ENGINE ---
            pegy_denominator = growth_percentage + yield_percentage
            pegy_ratio = pe / pegy_denominator if pegy_denominator > 0 else 0
            
            adjusted_price = raw_price * MACRO_SCALE_FACTOR
            fcf_yield_percentage = dynamic_fcf * MACRO_SCALE_FACTOR
            
            # --- UNIFIED MULTI-FACTOR STRATEGY MATRIX LOGIC ---
            is_low_pegy = pegy_ratio < PEGY_VALUE_THRESHOLD
            is_high_fcf = fcf_yield_percentage > FCF_YIELD_THRESHOLD
            
            if is_low_pegy and is_high_fcf:
                strategy_profile = "Strong Signal (Cash Generator)"
                cash_flow_insight = "High Quality Coverage"
                tier_priority = 1  
            elif not is_low_pegy and is_high_fcf:
                strategy_profile = "Expensive (Monitor Entry)"
                cash_flow_insight = "High Quality Coverage"
                tier_priority = 2  
            elif not is_low_pegy and not is_high_fcf:
                strategy_profile = "Premium Valuation"
                cash_flow_insight = "Stable / Low Coverage"
                tier_priority = 3  
            else:
                strategy_profile = "Value Trap (Cash-Strapped)"
                cash_flow_insight = "Weak Coverage Risk"
                tier_priority = 4  
            
            processed_assets.append({
                "ticker": ticker,
                "price": f"{adjusted_price:.2f}",
                "pe": f"{pe:.2f}",
                "growth": f"{growth_percentage:.2f}%",
                "divYield": f"{yield_percentage:.2f}%",
                "pegy": f"{pegy_ratio:.2f}",
                "fcfYield": f"{fcf_yield_percentage:.2f}%",
                "strategyProfile": strategy_profile,
                "cashFlowInsight": cash_flow_insight,
                "tier_priority": tier_priority,
                "score_sort": pegy_ratio # Standardizes the sorting key for browser compatibility
            })
            
        except Exception as e:
            print(f"Skipping processing parameters for {ticker}: {e}")
            continue

    # Execute structured multi-tier tuple sort
    # Sorts perfectly by Tier group first, then sequentially by raw PEGY ratio second
    processed_assets.sort(key=lambda x: (x["tier_priority"], x["score_sort"]))
    top_20 = processed_assets[:20]

    with open("top20.json", "w") as f:
        json.dump(top_20, f, indent=4)
        
    print(f"Saved structural tier priority top20.json artifact with {len(top_20)} entries.")

if __name__ == "__main__":
    compute_pegy_matrix()
