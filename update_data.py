import json
import time
import random
import yfinance as yf
import pandas as pd
import numpy as np
import logging

# --- MIXED MASTER SEED SHEET (Supports both Individual Stocks & ETFs) ---
MASTER_TICKERS = [
    "AAAP",
    "AACG",
    "AADR",
    "AAEQ",
    "AAL",
    "AALG",
    "AAME",
    "AAON",
    "AAPB",
    "AAPD",
    "AAPL",
    "AAPU",
    "AAUS",
    "SGA",
    "SGC",
    "SIEB",
    "SIFY",
    "SIGA",
    # <-- Paste the rest of your full ticker list here
]
MASTER_TICKERS = sorted(list(set(MASTER_TICKERS)))

MACRO_SCALE_FACTOR = 1.0450
PEGY_VALUE_THRESHOLD = 1.00
FCF_YIELD_THRESHOLD = 5.50

# Yield thresholds: 1.5% - 5.0% for Growth | >5.0% - 8.0% for Harvest
GROWTH_MIN_YIELD = 1.50
GROWTH_MAX_YIELD = 5.00
HARVEST_MAX_YIELD = 8.00

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_ticker_info_with_backoff(ticker, max_retries=5):
    """
    Safely extracts ticker info payload with randomized delays
    and adaptive backoff multipliers to handle API rate limits.
    """
    base_delay = 3
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(0.6, 1.5))
            ticker_object = yf.Ticker(ticker)
            info = ticker_object.info
            return ticker_object, info
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
                wait_time = (base_delay ** (attempt + 1)) + random.uniform(1.0, 3.0)
                logger.warning(
                    f"⚠️ [Rate Limited] Triggered on {ticker}. Pausing for {wait_time:.2f}s "
                    f"(Attempt {attempt+1}/{max_retries})..."
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {ticker}: {e}")
                raise e
    logger.error(f"Failed to fetch {ticker} after {max_retries} attempts.")
    return None, None


def get_dividend_growth_rate(ticker_obj):
    """Calculates the 5-year annualized physical cash dividend growth rate."""
    try:
        divs = ticker_obj.dividends
        if divs.empty or len(divs) < 4:
            logger.warning(f"Not enough dividend data for {ticker_obj.ticker}. Returning default CAGR.")
            return 5.0
        annual_divs = divs.resample('YE').sum()
        if len(annual_divs) < 5:
            logger.warning(f"Not enough annual dividend data for {ticker_obj.ticker}. Returning default CAGR.")
            return 5.0
        start_val = float(annual_divs.iloc[-5])
        end_val = float(annual_divs.iloc[-1])
        if start_val <= 0 or end_val <= 0:
            logger.warning(f"Invalid dividend values for {ticker_obj.ticker}. Returning default CAGR.")
            return 5.0
        cagr = ((end_val / start_val) ** (1 / 4) - 1) * 100
        if cagr <= 0.1 or cagr > 20.0 or np.isnan(cagr):
            logger.warning(f"Invalid CAGR for {ticker_obj.ticker}. Returning default CAGR.")
            return 5.0
        return cagr
    except Exception as e:
        logger.error(f"Error calculating dividend growth rate for {ticker_obj.ticker}: {e}")
        return 5.0


def check_performance_cagr(ticker_symbol, bulk_df):
    """Calculates historical 1, 5, and 10 year price growth vectors to confirm upward trends."""
    try:
        if isinstance(bulk_df.columns, pd.MultiIndex):
            if ticker_symbol in bulk_df.columns.levels[0]:
                hist = bulk_df[ticker_symbol].dropna(subset=['Close'])
            else:
                logger.warning(f"No data found for {ticker_symbol} in bulk data. Returning 0.0 and False.")
                return 0.0, False
        else:
            hist = bulk_df.dropna(subset=['Close'])

        if hist.empty or len(hist) < 252:
            logger.warning(f"Not enough historical data for {ticker_symbol}. Returning 0.0 and False.")
            return 0.0, False

        close = hist['Close']
        current_price = float(close.iloc[-1])

        val_1y = float(close.iloc[-252]) if len(close) >= 252 else float(close.iloc[0])
        val_5y = float(close.iloc[-1260]) if len(close) >= 1260 else float(close.iloc[0])
        val_10y = float(close.iloc[0])

        cagr_1 = ((current_price / val_1y) - 1) * 100 if val_1y > 0 else 0.0
        cagr_5 = ((current_price / val_5y) ** (1 / 5) - 1) * 100 if current_price > 0 and val_5y > 0 else 0.0
        cagr_10 = ((current_price / val_10y) ** (1 / 10) - 1) * 100 if current_price > 0 and val_10y > 0 else 0.0

        trends_upward = bool(current_price > val_1y and val_1y > val_5y)
        avg_cagr = float(cagr_1 + cagr_5 + cagr_10) / 3

        return avg_cagr, trends_upward
    except Exception as e:
        logger.error(f"Error checking performance CAGR for {ticker_symbol}: {e}")
        return 0.0, False


def compute_pegy_matrix():
    logger.info("Initializing Dual-Path Hybrid Ranking Pipeline for %d tickers...", len(MASTER_TICKERS))

    try:
        bulk_data = yf.download(MASTER_TICKERS, period="10y", group_by="ticker", progress=False)
    except Exception as e:
        logger.error(f"Bulk market feed failure: {e}")
        return

    growth_assets = []
    harvest_assets = []

    for ticker in MASTER_TICKERS:
        try:
            ticker_object, info = fetch_ticker_info_with_backoff(ticker)

            if not info or (info.get("trailingPE") is None and info.get("dividendYield") is None):
                logger.warning(f"Insufficient data for {ticker}. Skipping.")
                continue

            quote_type = info.get("quoteType", "").upper()
            is_etf = "ETF" in quote_type or "MUTUALFUND" in quote_type

            if is_etf:
                expense_ratio = info.get("expenseRatio") or 0.0
                if expense_ratio > 0.0050:
                    logger.warning(f"High expense ratio for {ticker}. Skipping.")
                    continue
                pb_ratio = info.get("priceToBook") or 1.8
                if pb_ratio <= 0 or np.isnan(pb_ratio):
                    logger.warning(f"Invalid P/B ratio for {ticker}. Using default value.")
                    pb_ratio = 1.8
                turnover = info.get("portfolioTurnover") or 0.20
                dynamic_fcf = (1.0 / pb_ratio) * (10.0 + turnover)
            else:
                market_cap = info.get("marketCap") or 0
                op_cashflow = info.get("operatingCashflow") or 0
                free_cash_flow = info.get("freeCashflow") or (op_cashflow * 0.75)

                if market_cap > 0 and free_cash_flow > 0:
                    dynamic_fcf = (free_cash_flow / market_cap) * 100.0
                else:
                    pb_ratio = info.get("priceToBook") or 2.5
                    if pb_ratio <= 0 or np.isnan(pb_ratio):
                        logger.warning(f"Invalid P/B ratio for {ticker}. Using default value.")
                        pb_ratio = 2.5
                    dynamic_fcf = (1.0 / pb_ratio) * 12.0

            # Normalize dividend yield cleanly
            if info.get("trailingAnnualDividendYield") is not None:
                yield_percentage = float(info["trailingAnnualDividendYield"]) * 100.0
            elif info.get("dividendYield") is not None:
                raw_yield = float(info["dividendYield"])
                yield_percentage = raw_yield * 100.0 if raw_yield < 0.20 else raw_yield
            else:
                yield_percentage = 0.0

            # Filter for 1.5% to 8.0% total range
            if yield_percentage < GROWTH_MIN_YIELD or yield_percentage > HARVEST_MAX_YIELD:
                logger.warning(f"Yield {yield_percentage:.2f}% out of range for {ticker}. Skipping.")
                continue

            try:
                if isinstance(bulk_data.columns, pd.MultiIndex):
                    hist_close = bulk_data[ticker]['Close'].dropna()
                else:
                    hist_close = bulk_data['Close'].dropna()

                if hist_close.shape[0] == 0:
                    logger.warning(f"No historical data for {ticker}. Skipping.")
                    continue
                current_price = float(hist_close.iloc[-1])
            except Exception as e:
                logger.error(f"Error fetching historical data for {ticker}: {e}")
                continue

            pe = info.get("trailingPE") or info.get("forwardPE") or 16.2
            if pe <= 2.0 or pe > 50.0 or np.isnan(pe):
                logger.warning(f"Invalid P/E ratio for {ticker}. Using default value.")
                pe = 16.2

            avg_cagr, is_trending_up = check_performance_cagr(ticker, bulk_data)
            growth_percentage = get_dividend_growth_rate(ticker_object)

            pegy_denominator = growth_percentage + yield_percentage
            if pegy_denominator <= 0:
                logger.warning(f"Invalid PEGY denominator for {ticker}. Using default value.")
                pegy_denominator = 1.0
            pegy_ratio = pe / pegy_denominator

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

            asset_payload = {
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
            }

            # Route into Growth (1.5% - 5.0%) vs. Harvest (>5.0% - 8.0%)
            if GROWTH_MIN_YIELD <= yield_percentage <= GROWTH_MAX_YIELD:
                growth_assets.append(asset_payload)
                logger.info(f"Hybrid Matrix Mapping -> {ticker} ({asset_type_label}) targeted to Growth [Tier {tier}]")
            elif GROWTH_MAX_YIELD < yield_percentage <= HARVEST_MAX_YIELD:
                harvest_assets.append(asset_payload)
                logger.info(f"Hybrid Matrix Mapping -> {ticker} ({asset_type_label}) targeted to Harvest [Tier {tier}]")

        except Exception as e:
            logger.error(f"Skipping {ticker} due to parsing anomaly: {e}")
            continue

    growth_assets.sort(key=lambda x: (x["tier_priority"], x["score_sort"]))
    harvest_assets.sort(key=lambda x: (x["tier_priority"], x["score_sort"]))

    final_output_payload = {
        "growth": growth_assets[:20],
        "harvest": harvest_assets[:20]
    }

    try:
        with open("top20.json", "w") as f:
            json.dump(final_output_payload, f, indent=4)
        logger.info(
            "Success! Saved %d Growth and %d Harvest assets to top20.json.",
            len(final_output_payload["growth"]),
            len(final_output_payload["harvest"])
        )
    except IOError as e:
        logger.error(f"Failed to write to top20.json: {e}")


if __name__ == "__main__":
    compute_pegy_matrix()
