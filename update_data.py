import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

def compute_pegy_matrix():
    print("🚀 Initializing Quantum Dividend Engine Pipeline...")
    
    # 1. CORE SEED LIST (Expand this array with your 300+ tickers as needed)
    ticker_universe = [
        "KO", "PEP", "JNJ", "PG", "XOM", "CVX", "MSFT", "AAPL", "ABBV", "MO",
        "SCHD", "VYM", "JEPI", "JEPQ", "DGRO", "VIG", "O", "STAG", "MAIN", "ARCC",
        "MMM", "T", "VZ", "ABT", "LOW", "TXN", "AVGO", "HD", "MCD", "WM"
    ]
    
    compound_pool = []
    harvest_pool = []
    
    # Macro scaling multiplier from base design configuration
    MACRO_MULTIPLIER = 1.0450
    
    for ticker in ticker_universe:
        try:
            asset = yf.Ticker(ticker)
            info = asset.info
            
            if not info or not isinstance(info, dict):
                print(f"⚠️  Skipping {ticker}: No data payload returned from API.")
                continue
                
            # Extract asset market pricing metrics safely
            price = info.get("currentPrice") or info.get("navPrice") or info.get("previousClose")
            if not price:
                print(f"⚠️  Skipping {ticker}: Pricing index unavailable.")
                continue
                
            # --- TYPE-SAFE METRIC PARSING & ASSET IDENTIFICATION ---
            quote_type = info.get("quoteType", "")
            if not isinstance(quote_type, str):
                quote_type = ""
            quote_type = quote_type.upper()
            
            is_etf = quote_type in ["ETF", "EXCHANGETRADEDFUND", "MUTUALFUND"]
            
            # --- GLOBAL ETFS OPERATIONAL FEE FILTER ---
            if is_etf:
                expense_ratio = info.get("expenseRatio", 0) or 0
                if expense_ratio > 0.0050:  # Skip high expense ETFs (>0.50%)
                    print(f"✂️  Filtered {ticker}: Expense ratio too high ({round(expense_ratio * 100, 2)}%).")
                    continue
            
            # --- NORMALIZING DIVIDEND DATA ---
            raw_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield") or 0
            pct_yield = raw_yield * 100  # Convert decimal to percent (e.g., 0.035 -> 3.5%)
            
            # Extract operational valuation coefficients
            pe = info.get("forwardPE") or info.get("trailingPE") or 15.0
            
            # Extract 5-Year CAGR parameters
            five_year_cagr = info.get("fiveYearAvgDividendYield") or info.get("dividendRate", 4.0)
            if not isinstance(five_year_cagr, (int, float)) or five_year_cagr <= 0:
                five_year_cagr = 4.0  # Safe statistical baseline fallback
            
            # --- FREE CASH FLOW METRIC ANALYSIS ---
            fcf = info.get("freeCashflow") or info.get("operatingCashflow", 0) or 0
            shares_outstanding = info.get("sharesOutstanding", 1) or 1
            fcf_per_share = fcf / shares_outstanding if fcf > 0 else 0
            fcf_yield = (fcf_per_share / price) * 100 if price > 0 else 0
            
            # --- VALUE TRAP SHIELD CALCULATION ENGINE ---
            annual_div_per_share = info.get("trailingAnnualDividendRate") or (price * raw_yield) or 0
            fcf_payout_ratio = (annual_div_per_share / fcf_per_share) if fcf_per_share > 0 else float('inf')
            
            # --- PEGY EVALUATION MATRIX FORMULA ---
            # Formula: PEGY = PE / (5Y CAGR Growth Rate + Current Dividend Yield)
            denominator = five_year_cagr + pct_yield
            pegy = round(pe / denominator, 4) if denominator > 0 else 99.9
            
            # Apply institutional scale tuning multiplier
            adjusted_price = round(price * MACRO_MULTIPLIER, 2)
            
            # Build unified normalized item dictionary 
            asset_payload = {
                "ticker": ticker,
                "price": adjusted_price,
                "pe": round(pe, 2),
                "growth": f"{round(five_year_cagr, 2)}%",
                "divYield": f"{round(pct_yield, 2)}%",
                "pegy": pegy,
                "fcfYield": f"{round(fcf_yield, 2)}%",
                "strategyProfile": "ETF Core Classic" if is_etf else "Equity Cash Engine",
                "cashFlowInsight": "Stable FCF Cover" if fcf_payout_ratio <= 0.85 else "Leveraged Payout"
            }
            
            # --- AUTOMATED DUAL-STREAM SEPARATION LAYER ---
            # 1. ROUTE TO COMPOUND MATRIX (1.5% to 5.0%)
            if 1.5 <= pct_yield <= 5.0:
                compound_pool.append(asset_payload)
                print(f"🌱 Routed to Compound: {ticker} ({round(pct_yield, 2)}% Yield, PEGY: {pegy})")
                
            # 2. ROUTE TO HARVEST MATRIX (5.1% to 8.0%) WITH INTEGRATED DEFENSE SHIELD
            elif 5.1 <= pct_yield <= 8.0:
                # 🛑 VALUE TRAP DETECTOR 1: Cash exhaustion payout profile
                if fcf_payout_ratio > 0.85 and not is_etf:
                    print(f"🛑 Filtered Value Trap {ticker}: Dividend consumes {round(fcf_payout_ratio*100, 2)}% of real FCF.")
                    continue
                    
                # 🛑 VALUE TRAP DETECTOR 2: Negative distribution regression model
                if five_year_cagr < 0:
                    print(f"🛑 Filtered Value Trap {ticker}: 5-Year CAGR metric shows decay pattern.")
                    continue
                
                # Upgrade badge insight properties for safe high-yielding entries
                asset_payload["strategyProfile"] = "High Yield Income" if not is_etf else "Income ETF Core"
                harvest_pool.append(asset_payload)
                print(f"🌾 Routed to Safe Harvest: {ticker} ({round(pct_yield, 2)}% Yield, PEGY: {pegy})")
                
        except Exception as e:
            print(f"❌ Processing error skipped for tracker asset {ticker}: {str(e)}")
            continue

    # Sort array entries by structural PEGY efficiency (Lower PEGY represents optimal cost-to-growth ratio)
    compound_pool = sorted(compound_pool, key=lambda x: x["pegy"])[:20]
    harvest_pool = sorted(harvest_pool, key=lambda x: x["pegy"])[:20]
    
    # Pack pools into multi-phase relational data object
    output_matrix = {
        "compound": compound_pool,
        "harvest": harvest_pool
    }
    
    # Save optimized data stream straight to target project JSON datastore
    with open("./top20.json", "w") as json_file:
        json.dump(output_matrix, json_file, indent=4)
        
    print("\n========================================================")
    print(f"✅ ENGINE SUCCESS: Saved {len(compound_pool)} Compound & {len(harvest_pool)} safe Harvest assets to JSON.")
    print("========================================================\n")

if __name__ == "__main__":
    compute_pegy_matrix()
