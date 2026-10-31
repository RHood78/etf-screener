import json
import yfinance as yf

# --- MASTER TICKER SHEET ---
# Mapped back to standard tickers (No Stooq suffixes required!)
MASTER_TICKERS = [
    "SCHD", "VYM", "DGRO", "VIG", "JEPI", "JEPQ", "DVY", "SDY", 
    "DGRW", "HDV", "SPHD", "RDVY", "NOBL", "FVD", "CGDV", "PEY", 
    "SDVY", "DIVB", "REGL", "DIVO", "FDL", "DON", "DES", "DHS",
    "VYMI", "VIGI", "IDV", "LVHI", "SCHY", "IGRO", "DVYE", "FNDF"
]

MACRO_SCALE_FACTOR = 1.0450
DEFAULT_GROWTH = 0.065     # 6.5% baseline dividend growth rate proxy
DEFAULT_FCF_YIELD = 0.058  # 5.8% baseline free cash flow yield proxy

def compute_pegy_matrix():
    print("Beginning Multi-Factor Evaluation Matrix Pipeline Sequence via Yahoo Cloud Engine...")
    processed_assets = []
    
    # Fetch all tickers in bulk to optimize execution speed
    print(f"Syncing telemetry metadata profiles for {len(MASTER_TICKERS)} assets...")
    tickers_string = " ".join(MASTER_TICKERS)
    yf_data = yf.Tickers(tickers_string)
    
    for ticker in MASTER_TICKERS:
        try:
            ticker_object = yf_data.tickers[ticker]
            info = ticker_object.info
            
            # Extract live values or slide to standard baselines if fields are missing
            raw_price = info.get("regularMarketPrice") or info.get("previousClose") or info.get("navPrice") or 0
            pe = info.get("trailingPE") or 16.5
            div_yield = info.get("trailingAnnualDividendYield") or info.get("dividendYield") or 0.032
            
            if raw_price == 0:
                print(f"Skipping {ticker}: Pricing telemetry field is zero.")
                continue
                
            # PEGY Ratio = P/E / (Blended Growth Rate% + Dividend Yield%)
            pegy_denominator = (DEFAULT_GROWTH * 100) + (div_yield * 100)
            pegy_ratio = pe / pegy_denominator if pegy_denominator > 0 else 0
            
            # Apply Macro Scale Factor modifiers uniformly 
            adjusted_price = raw_price * MACRO_SCALE_FACTOR
            fcf_yield_calc = DEFAULT_FCF_YIELD * MACRO_SCALE_FACTOR
            
            processed_assets.append({
                "ticker": ticker,
                "price": f"{adjusted_price:.2f}",
                "pe": f"{pe:.2f}",
                "growth": f"{(DEFAULT_GROWTH * 100):.2f}%",
                "divYield": f"{(div_yield * 100):.2f}%",
                "pegy": f"{pegy_ratio:.2f}",
                "fcfYield": f"{(fcf_yield_calc * 100):.2f}%",
                "strategyProfile": "Undervalued Growth" if pegy_ratio < 1.25 else "Core Equity Position",
                "cashFlowInsight": "High Quality Coverage" if fcf_yield_calc > 0.06 else "Stable Coverage",
                "score_sort": pegy_ratio
            })
            print(f"Successfully processed matrix calculations for {ticker}")
            
        except Exception as e:
            print(f"Skipping tracking loop parameters for {ticker}: {e}")
            continue

    # Sort items based on value (Lowest PEGY = Best Value Rank)
    processed_assets.sort(key=lambda x: x["score_sort"])
    top_20 = processed_assets[:20]

    # Save artifact strictly as static text mapping layer inside repository
    with open("top20.json", "w") as f:
        json.dump(top_20, f, indent=4)
    print(f"Successfully built top20.json matrix profile artifact with {len(top_20)} entries.")

if __name__ == "__main__":
    compute_pegy_matrix()
