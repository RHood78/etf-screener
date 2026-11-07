import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

def compute_pegy_matrix():
    print("Initializing Quantum Dividend Engine Pipeline...")
    
    # 1. Define your initial asset universe seed list (stocks and ETFs)
    ticker_universe = [
        "KO", "PEP", "JNJ", "PG", "XOM", "CVX", "MSFT", "AAPL", "ABV", "MO",
        "SCHD", "VYM", "JEPI", "JEPQ", "DGRO", "VIG", "O", "STAG", "MAIN", "ARCC"
        # ... rest of your 300+ asset list goes here
    ]
    
    compound_pool = []
    harvest_pool = []
    
    # Macro scaling multiplier from your base application profile
    MACRO_MULTIPLIER = 1.0450
    
    for ticker in ticker_universe:
        try:
            asset = yf.Ticker(ticker)
            info = asset.info
            
            # Extract basic operational metrics safely
            price = info.get("currentPrice") or info.get("navPrice") or info.get("previousClose")
            if not price:
                continue
                
            # Determine asset category rules
            quote_type = info.get("quoteType", "").upper()
            is_etf = quote_type in ["ETF", "EXCHANGETRADEDFUND"]
            
            # --- GLOBAL ETFS SCREENING RULES ---
            if is_etf:
                expense_ratio = info.get("expenseRatio", 0)
                if expense_ratio > 0.0050: # Exclude ETFs with expense ratios > 0.50%
                    continue
            
            # --- METRIC PARSING & NORMALIZATION ---
            # Extract raw yield (represented as a decimal from yfinance, e.g., 0.035)
            raw_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield") or 0
            pct_yield = raw_yield * 100 # Convert to percentage form (3.5%)
            
            # Forward P/E or trailing fallback
            pe = info.get("forwardPE") or info.get("trailingPE") or 15.0
            
            # 5-Year Dividend Growth CAGR extraction
            # Real-world fallback logic for your engine data structures
            growth_rate = info.get("dividendRate", 0) 
            # Simplified proxy modeling for your engine matrix
            five_year_cagr = info.get("fiveYearAvgDividendYield", 4.0) 
            
            # Free Cash Flow Analysis Metrics
            fcf = info.get("freeCashflow") or info.get("operatingCashflow", 0)
            shares_outstanding = info.get("sharesOutstanding", 1)
            fcf_per_share = fcf / shares_outstanding if fcf else 0
            fcf_yield = (fcf_per_share / price) * 100 if price > 0 else 0
            
            # --- VALUE TRAP EXTRACTION MATH (THE SAFETY CHECK) ---
            # Total dividends paid per share annually
            annual_div_per_share = info.get("trailingAnnualDividendRate") or (price * raw_yield)
            
            # Compute FCF Payout Ratio
            fcf_payout_ratio = (annual_div_per_share / fcf_per_share) if fcf_per_share > 0 else float('inf')
            
            # Compute final mathematical PEGY valuation metric
            # Formula: PEGY = PE / (Growth Rate + Dividend Yield)
            denominator = five_year_cagr + pct_yield
            pegy = round(pe / denominator, 4) if denominator > 0 else 99.9
            
            # Scale and construct target structural dictionary
            asset_payload = {
                "ticker": ticker,
                "price": round(price, 2),
                "pe": round(pe, 2),
                "growth": f"{round(five_year_cagr, 2)}%",
                "divYield": f"{round(pct_yield, 2)}%",
                "pegy": pegy,
                "fcfYield": f"{round(fcf_yield, 2)}%",
                "strategyProfile": "ETF Core Classic" if is_etf else "Equity Cash Engine",
                "cashFlowInsight": "Stable FCF Cover" if fcf_payout_ratio <= 0.85 else "Leveraged Payout"
            }
            
            # --- SPLIT ASSIGNMENT MATRIX ---
            # 1. COMPOUND PHASE ROUTING (1.5% - 5.0%)
            if 1.5 <= pct_yield <= 5.0:
                compound_pool.append(asset_payload)
                
            # 2. HARVEST PHASE ROUTING (5.1% - 8.0%) WITH INTEGRATED SAFETY ENFORCEMENT
            elif 5.1 <= pct_yield <= 8.0:
                # 🛑 VALUE TRAP SHIELD 🛑
                # Filter Out Rule 1: Dividend is structurally unsustainable out of real free cash flow
                if fcf_payout_ratio > 0.85 and not is_etf: 
                    print(print(f"Skipping potential value trap {ticker}: FCF Payout too high ({round(fcf_payout_ratio*100, 2)}%)"))
                    continue
                
                # Filter Out Rule 2: Negative trajectory signals a broken dividend model
                if five_year_cagr < 0:
                    print(f"Skipping potential value trap {ticker}: Negative Growth Trend")
                    continue
                
                # If it survives, upgrade badge insight parameters and route to Harvest
                asset_payload["strategyProfile"] = "High Yield Income" if not is_etf else "Income ETF Core"
                harvest_pool.append(asset_payload)
                
        except Exception as e:
            print(f"Processing error skipped for ticker {ticker}: {str(e)}")
            continue

    # Sort arrays ascending by PEGY (Lower PEGY means higher value efficiency)
    compound_pool = sorted(compound_pool, key=lambda x: x["pegy"])[:20]
    harvest_pool = sorted(harvest_pool, key=lambda x: x["pegy"])[:20]
    
    # Structure output into unified payload containing both states
    output_matrix = {
        "compound": compound_pool,
        "harvest": harvest_pool
    }
    
    # Save the dual-stream dataset to disc for app.js to instantly grab
    with open("./top20.json", "w") as json_file:
        json.dump(output_matrix, json_file, indent=4)
        
    print(f"Matrix run success. Saved {len(compound_pool)} Compound assets and {len(harvest_pool)} safe Harvest assets.")

if __name__ == "__main__":
    compute_pegy_matrix()
