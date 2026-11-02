import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- MIXED MASTER SEED SHEET (Supports both Individual Stocks & ETFs) ---
MASTER_TICKERS = [
    # --- Top Liquid US/Global ETFs ---
    "SCHD", "VIG", "VYM", "DGRO", "NOBL", "SPHD", "VXUS", "VNQ",
    # --- Top Premium Blue-Chip Dividend Stocks ---
    "AAPL", "MSFT", "KO", "PEP", "JNJ", "PG", "XOM", "CVX", "MMM", "O"
]
MASTER_TICKERS = sorted(list(set(MASTER_TICKERS)))

MACRO_SCALE_FACTOR = 1.0450
PEGY_VALUE_THRESHOLD = 1.00
FCF_YIELD_THRESHOLD = 5.50

def get_dividend_growth_rate(ticker_obj):
    """Calculates the 5-year annualized physical cash dividend growth rate."""
    try:
        divs = ticker_obj.dividends
        if divs.empty or len(divs) < 4:
            return 5.0
        annual_divs = divs.resample('YE').sum()
        if len(annual_divs) < 5:
            return 5.0
        start_val = annual_divs.iloc[-5]
        end_val = annual_divs.iloc[-1]
        if start_val <= 0 or end_val <= 0:
            return 5.0
        cagr = ((end_val / start_val) ** (1/4) - 1) * 100
        if cagr <= 0.1 or cagr > 20.0 or np.isnan(cagr):
            return 5.0
        return cagr
    except:
        return 5.0

def check_performance_cagr(ticker_symbol, bulk_df):
    """Calculates historical 1, 5, and 10 year price growth vectors to confirm upward trends."""
    try:
        if ticker_symbol not in bulk_df.columns.levels:
            return 0.0, False
            
        hist = bulk_df[ticker_symbol].dropna(subset=['Close'])
        if hist.empty or len(hist) < 252:
            return 0.0, False
        
        close = hist['Close']
        current_price = float(close.iloc[-1])
        
        val_1y = float(close.iloc[-252]) if len(close) >= 252 else float(close.iloc[0])
        val_5y = float(close.iloc[-1260]) if len(close) >= 1260 else float(close.iloc[0])
        val_10y = float(close.iloc[0])
        
        cagr_1 = ((current_price / val_1y) - 1) * 100 if val_1y > 0 else 0.0
        cagr_5 = ((current_price / val_5y) ** (1/5) - 1) * 100 if current_price > 0 and val_5y > 0 else 0.0
        cagr_10 = ((current_price / val_10y) ** (1/10) - 1) * 100 if current_price > 0 and val_10y > 0 else 0.0
        
        trends_upward = (current_price > val_1y) and (val_1y > val_5y)
        avg_cagr = (cagr_1 + cagr_5 + cagr_10) / 3
        
        return avg_cagr, trends_upward
    except:
        return 0.0, False

def compute_pegy_matrix():
    print(f"Initializing Dual-Path Hybrid Ranking Pipeline for {len(MASTER_TICKERS)} tickers...")
    
    try:
        bulk_data = yf.download(MASTER_TICKERS, period="10y", group_by="ticker", progress=False)
    except Exception as e:
        print(f"Bulk market feed failure: {e}")
        return

    processed_assets = []
    
    for ticker in MASTER_TICKERS:
        try:
            ticker_object = yf.Ticker(ticker)
            info = ticker_object.info
            if not info:
                continue

            # --- 1. DUAL-PATH ASSET IDENTIFICATION ENGINE ---
            # Auto-detects whether the asset is a Fund/ETF or a Corporate Stock
            quote_type = info.get("quoteType", "").upper()
            is_etf = "ETF" in quote_type or "MUTUALFUND" in quote_type

            # --- 2. EXPENSE RATIO GATING LAYER ---
            if is_etf:
                expense_ratio = info.get("expenseRatio", 0.0) or 0.0
                if expense_ratio > 0.0050: # Filters out funds charging over 0.50%
                    continue
            else:
                # Individual corporate stocks do not have expense ratios; assign zero friction
                expense_ratio = 0.0

            # --- 3. UNIVERSAL DISTRIBUTION BANDWIDTH FILTERS ---
            yield_indicator = info.get("trailingAnnualDividendYield") or info.get("dividendYield") or 0.0
            if yield_indicator >= 0.20: 
                yield_indicator = yield_indicator / 100.0 if yield_indicator > 1.0 else yield_indicator * 0.10
            
            yield_percentage = yield_indicator * 100.0
            # Broaden target gate slightly to 1.5% - 5.0% to allow blue-chip stocks to co-exist with high-yield ETFs
            if yield_percentage < 1.5 or yield_percentage > 5.0:
                continue

            # --- 4. VALUATION MULTIPLIERS (P/E RATIO) ---
            if ticker not in bulk_data.columns.levels:
                continue
            hist_close = bulk_data[ticker]['Close'].dropna()
            if hist_close.empty:
                continue
            current_price = float(hist_close.iloc[-1])

            pe = info.get("trailingPE") or info.get("forwardPE") or 16.2
            if pe <= 2.0 or pe > 50.0 or np.isnan(pe): 
                pe = 16.2
            
            # --- 5. PERFORMANCE AND MOMENTUM ENGINE ---
            avg_cagr, is_trending_up = check_performance_cagr(ticker, bulk_data)
            growth_percentage = get_dividend_growth_rate(ticker_object)
                
            # --- 6. DUAL-PATH FREE CASH FLOW (FCF) YIELD ENGINE ---
            if is_etf:
                # ETF Cash Path: Use a Price-to-Book and Turnover proxy model
                pb_ratio = info.get("priceToBook") or 1.8
                if pb_ratio <= 0 or np.isnan(pb_ratio): pb_ratio = 1.8
                turnover = info.get("portfolioTurnover", 0.20) or 0.20
                dynamic_fcf = (1.0 / pb_ratio) * (10.0 + turnover)
            else:
                # Stock Cash Path: Calculate TRUE Corporate FCF Yield directly from the balance sheet
                market_cap = info.get("marketCap", 0)
                # Fallback path if explicit FCF cash flow fields are withheld by yfinance
                free_cash_flow = info.get("freeCashflow") or info.get("operatingCashflow", 0) * 0.75
                if market_cap > 0 and free_cash_flow > 0:
                    dynamic_fcf = (free_cash_flow / market_cap) * 100.0
                else:
                    # Leverage P/B proxy as clean stock fallback if fundamentals are blank
                    pb_ratio = info.get("priceToBook", 2.5) or 2.5
                    dynamic_fcf = (1.0 / pb_ratio) * 12.0

            if dynamic_fcf < 1.0 or dynamic_fcf > 20.0 or np.isnan(dynamic_fcf):
                dynamic_fcf = 5.8
            
            # --- 7. CORE STANDARDIZED SCORING MATRIX ---
            pegy_denominator = growth_percentage + yield_percentage
            pegy_ratio = pe / pegy_denominator if pegy_denominator > 0 else 99.0
            
            adjusted_price = current_price * MACRO_SCALE_FACTOR
            fcf_yield_percentage = dynamic_fcf * MACRO_SCALE_FACTOR
            
            is_low_pegy = pegy_ratio < PEGY_VALUE_THRESHOLD
            is_high_fcf = fcf_yield_percentage > FCF_YIELD_THRESHOLD
            meets_cagr_target = avg_cagr >= 5.0  
            
            # --- 8. TIER PRIORITIZATION ASSIGNMENTS ---
            if is_low_pegy and is_high_fcf and is_trending_up and meets_cagr_target:
                profile, insight, tier = "Strong Signal (Cash Generator)", "High Quality Coverage", 1  
            elif is_high_fcf and is_trending_up:
                profile, insight, tier = "Expensive (Monitor Entry)", "High Quality Coverage", 2  
            elif is_low_pegy and not is_high_fcf:
                profile, insight, tier = "Value Trap (Cash-Strapped)", "Weak Coverage Risk", 4  
            else:
                profile, insight, tier = "Premium Valuation", "Stable / Low Coverage", 3  
            
            # Append instrument asset tags to your dashboard payload strings
            asset_type_label = "ETF" if is_etf else "Stock"
            
            processed_assets.append({
                "ticker": ticker,
                "price": f"{adjusted_price:.2f}",
                "pe": f"{pe:.2f}",
                "growth": f"{growth_percentage:.2f}%",
                "divYield": f"{yield_percentage:.2f}%",
                "pegy": f"{pegy_ratio:.2f}",
                "fcfYield": f"{fcf_yield_percentage:.2f}%",
                "strategyProfile": f"{profile} [{asset_type_label}]",
                "cashFlowInsight": insight,
                "tier_priority": tier,
                "score_sort": pegy_ratio 
            })
            print(f"Hybrid Matrix Mapping -> {ticker} ({asset_type_label}) assigned to Tier {tier}")
            
        except Exception as e:
            print(f"Skipping {ticker}: {e}")
            continue

    processed_assets.sort(key=lambda x: (x["tier_priority"], x["score_sort"]))
    top_20 = processed_assets[:20]

    with open("top20.json", "w") as f:
        json.dump(top_20, f, indent=4)
        
    print(f"\nSuccess! Standardized hybrid matrix saved seamlessly to top20.json.")

if __name__ == "__main__":
    compute_pegy_matrix()
