import json
import time
import random
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- MIXED MASTER SEED SHEET (Supports both Individual Stocks & ETFs) ---
# Temporarily shortened for token efficiency during configuration tests
MASTER_TICKERS = [
    "AAAP", "AACG", "AADR", "AAEQ", "AAL", "AALG", "AAME", "AAON", "AAPB", "AAPD",
    "AAPL", "AAPU", "AAUS", "SGA", "SGC", "SIEB", "SIFY", "SIGA",
]

MASTER_TICKERS = sorted(list(set(MASTER_TICKERS)))

MACRO_SCALE_FACTOR = 1.0450
PEGY_VALUE_THRESHOLD = 1.00
FCF_YIELD_THRESHOLD = 5.50

# Global shared connection session to bypass GitHub Actions rate limits
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def fetch_ticker_info_with_backoff(ticker, max_retries=5):
    """
    Safely extracts ticker info payload with randomized delays 
    and adaptive backoff multipliers to handle API rate limits.
    """
    base_delay = 3
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(0.6, 1.5))
            ticker_object = yf.Ticker(ticker, session=session)
            info = ticker_object.info
            return ticker_object, info
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
                wait_time = (base_delay ** (attempt + 1)) + random.uniform(1.0, 3.0)
                print(f"⚠️ [Rate Limited] Triggered on {ticker}. Pausing execution for {wait_time:.2f}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e
    return None, None

def get_dividend_growth_rate(ticker_obj):
    """Calculates the 5-year annualized physical cash dividend growth rate."""
    try:
        divs = ticker_obj.dividends
        if divs.empty or len(divs) < 4:
            return 5.0
        annual_divs = divs.resample('YE').sum()
        if len(annual_divs) < 5:
            return 5.0
        start_val = float(annual_divs.iloc[-5])
        end_val = float(annual_divs.iloc[-1])
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
        if isinstance(bulk_df.columns, pd.MultiIndex):
            if ticker_symbol in bulk_df.columns.levels[0]:
                hist = bulk_df[ticker_symbol].dropna(subset=['Close'])
            else:
                return 0.0, False
        else:
            hist = bulk_df.dropna(subset=['Close'])
            
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
        
        trends_upward = bool(current_price > val_1y and val_1y > val_5y)
        avg_cagr = float(cagr_1 + cagr_5 + cagr_10) / 3
        
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
            ticker_object, info = fetch_ticker_info_with_backoff(ticker)
            
            if not info or (info.get("trailingPE") is None and info.get("dividendYield") is None):
                continue

            quote_type = info.get("quoteType", "").upper()
            is_etf = "ETF" in quote_type or "MUTUALFUND" in quote_type

            if is_etf:
                expense_ratio = info.get("expenseRatio", 0.0) or 0.0
                if expense_ratio > 0.0050: 
                    continue
            else:
                expense_ratio = 0.0

            yield_indicator = info.get("trailingAnnualDividendYield") or info.get("dividendYield") or 0.0
            if yield_indicator >= 0.20: 
                yield_indicator = yield_indicator / 100.0 if yield_indicator > 1.0 else yield_indicator * 0.10
            
            yield_percentage = yield_indicator * 100.0
            
            # ADJUSTED CAP: Expanded maximum range gate from 5.0 to 8.0 
            # to capture high-yield and covered-call Harvest investments.
            if yield_percentage < 1.5 or yield_percentage > 8.0:
                continue

            try:
                if isinstance(bulk_data.columns, pd.MultiIndex):
                    hist_close = bulk_data[ticker]['Close'].dropna()
                else:
                    hist_close = bulk_data['Close'].dropna()
                
                if hist_close.shape[0] == 0:
                    continue
                current_price = float(hist_close.iloc[-1])
            except:
                continue

            pe = info.get("trailingPE") or info.get("forwardPE") or 16.2
            if pe <= 2.0 or pe > 50.0 or np.isnan(pe): 
                pe = 16.2
            
            avg_cagr, is_trending_up = check_performance_cagr(ticker, bulk_data)
            growth_percentage = get_dividend_growth_rate(ticker_object)
                
            if is_etf:
                pb_ratio = info.get("priceToBook") or 1.8
                if pb_ratio <= 0 or np.isnan(pb_ratio): pb_ratio = 1.8
                turnover = info.get("portfolioTurnover", 0.20) or 0.20
                dynamic_fcf = (1.0 / pb_ratio) * (10.0 + turnover)
            else:
                market_cap = info.get("marketCap", 0)
                free_cash_flow = info.get("freeCashflow") or info.get("operatingCashflow", 0) * 0.75
                if market_cap > 0 and free_cash_flow > 0:
                    dynamic_fcf = (free_cash_flow / market_cap) * 100.0
                else:
                    pb_ratio = info.get("priceToBook", 2.5) or 2.5
                    dynamic_fcf = (1.0 / pb_ratio) * 12.0

            if dynamic_fcf < 1.0 or dynamic_fcf > 20.0 or np.isnan(dynamic_fcf):
                dynamic_fcf = 5.8
            
            pegy_denominator = growth_percentage + yield_percentage
            pegy_ratio = pe / pegy_denominator if pegy_denominator > 0 else 99.0
            
            adjusted_price = current_price * MACRO_SCALE_FACTOR
            fcf_yield_percentage = dynamic_fcf * MACRO_SCALE_FACTOR
            
            is_low_pegy = bool(pegy_ratio < PEGY_VALUE_THRESHOLD)
            is_high_fcf = bool(fcf_yield_percentage > FCF_YIELD_THRESHOLD)
            meets_cagr_target = bool(avg_cagr >= 5.0)
            
            if is_low_pegy and is_high_fcf and is_trending_up and meets_cagr_target:
                profile, insight, tier = "Strong Signal (Cash Generator)", "High Quality Coverage", 1  
            elif is_high_fcf and is_trending_up:
                profile, insight, tier = "Expensive (Monitor Entry)", "High Quality Coverage", 2  
            elif is_low_pegy and not is_high_fcf:
                profile, insight, tier = "Value Trap (Cash-Strapped)", "Weak Coverage Risk", 4  
            else:
                profile, insight, tier = "Premium Valuation", "Stable / Low Coverage", 3  
            
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
                "tier_priority": int(tier),
                "score_sort": float(pegy_ratio) 
            })
            print(f"Hybrid Matrix Mapping -> {ticker} ({asset_type_label}) assigned to Tier {tier}")
            
        except Exception as e:
            print(f"Skipping {ticker} due to parsing anomaly: {e}")
            continue

    processed_assets.sort(key=lambda x: (x["tier_priority"], x["score_sort"]))
    top_20 = processed_assets[:20]

    with open("top20.json", "w") as f:
        json.dump(top_20, f, indent=4)
        
    print(f"\nSuccess! Standardized hybrid matrix saved seamlessly to top20.json.")

if __name__ == "__main__":
    compute_pegy_matrix()
