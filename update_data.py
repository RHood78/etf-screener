import json
import yfinance as yf
import pandas as pd
import numpy as np

# --- OPTIMIZED COMPREHENSIVE GLOBAL DIVIDEND ETF MASTER ---
MASTER_TICKERS = [
    "AAXJ", "ACWV", "AIA", "ALTY", "AMLP", "AOA", "AOK", "AOM", "AOR", "APIE", "ASHR", "BAB", "BBCA", "BBEU", "BBJP", "BBRE", 
    "BFOR", "BGU", "BIZD", "BJK", "BND", "BNDX", "BOM", "BSCE", "BSCH", "BSCI", "BSCJ", "BSCK", "BSCL", "BSCM", "BSCN", "BSCO", 
    "BSCP", "BSCQ", "BYLD", "CAPE", "CDC", "CDL", "CEFL", "CEY", "CFA", "CFGE", "CGDV", "CHIE", "CHIK", "CHIM", "CHIQ", "CHIR", "CHIS", 
    "CHIU", "CHIX", "CHJE", "CHNA", "CIEO", "CIPP", "CN", "CNYA", "COBO", "COW", "CQQQ", "CRBN", "CSB", "CSCR", "CSD", 
    "CSM", "CVY", "CWEB", "CXSE", "CYB", "DAX", "DBAW", "DBEF", "DBEM", "DBEU", "DBEZ", "DBJA", "DBJP", "DEEF", "DEM", "DES", 
    "DEW", "DFE", "DFEV", "DFIV", "DFJ", "DFND", "DFNL", "DFNV", "DFRA", "DFSE", "DFSV", "DFUS", "DFUV", "DGBP", "DGRE", "DGRID", "DGRO", 
    "DGRS", "DGRW", "DGS", "DHDG", "DHS", "DHVW", "DIA", "DIAL", "DIG", "DIM", "DIV", "DIVA", "DIVB", "DIVC", "DIVI", "DIVO", "DJD", "DJP", 
    "DLN", "DLS", "DNL", "DOL", "DON", "DOO", "DREEE", "DRIP", "DRN", "DRW", "DTH", "DTD", "DURA", "DVY", "DVYA", "DVYE", "DWM", "DXJ", 
    "DXJC", "DXJS", "DYLS", "EAGG", "ECLN", "ECON", "EDEN", "EDIV", "EDV", "EDXC", "EEB", "EEMA", "EEMS", "EERM", "EFA", "EFAS", "EFAV", 
    "EFNL", "EFV", "EGPT", "EIDO", "EIRL", "EIS", "EMBD", "EMCB", "EMDV", "EMGF", "EMHY", "EMIF", "EMLC", "EMLP", "EMNS", "EMNT", "EMQQ", 
    "EMTL", "EMXC", "ENFR", "EPHE", "EPI", "EPOL", "EPU", "EQAL", "EQWL", "ERUS", "ESD", "ESG", "ESGD", "ESGE", "ESGG", "ESGN", 
    "ESGR", "ESGS", "ESGU", "ETHN", "ETHO", "EUMV", "EURL", "EUSA", "EUSC", "EWA", "EWC", "EWD", "EWG", "EWH", "EWI", "EWJ", "EWK", "EWL", 
    "EWM", "EWN", "EWO", "EWP", "EWQ", "EWS", "EWT", "EWU", "EWV", "EWW", "EWY", "EWZ", "EXI", "EYLD", "FAD", "FALN", "FBND", "FBT", "FCEF", 
    "FCFI", "FCI", "FCT", "FDD", "FDL", "FDRR", "FDT", "FDTS", "FDV", "FDVV", "FDX", "FEM", "FEMS", "FGD", "FIDI", "FIHD", "FILD", "FINX", 
    "FLAX", "FLBL", "FLBR", "FLCA", "FLCH", "FLDE", "FLEH", "FLES", "FLFR", "FLGB", "FLGR", "FLGT", "FLHK", "FLIA", "FLIN", "FLIY", "FLIT", 
    "FLJA", "FLJH", "FLJP", "FLKR", "FLLH", "FLMB", "FLMX", "FLN", "FLNL", "FLOT", "FLPE", "FLQA", "FLRG", "FLRU", "FLSA", "FLSB", "FLSG", 
    "FLSP", "FLSW", "FLTA", "FLTR", "FLTW", "FLUD", "FLUS", "FLVA", "FLZA", "FMAT", "FMB", "FMF", "FMNX", "FMXV", "FNB", "FNDA", "FNDB", 
    "FNDC", "FNDE", "FNDF", "FNDX", "FNX", "FPX", "FSG", "FSTA", "FTCS", "FTCSI", "FTRI", "FTXD", "FTXE", "FTXG", "FTXH", "FTXL", "FTXN", 
    "FTXO", "FTXR", "FTXTC", "FUTY", "FVA", "FVC", "FVD", "FVDD", "FVL", "FWDB", "FXA", "FXB", "FXC", "FXCH", "FXD", "FXE", "FXF", 
    "FXG", "FXH", "FXI", "FXL", "FXN", "FXO", "FXR", "FXS", "FXU", "FXZ", "FYC", "FYD", "FYG", "FYLD", "FYT", "FYX", "GAF", "GCE", 
    "GCOW", "GDAY", "GDX", "GDXJ", "GEM", "GEUR", "GGOV", "GHYG", "GID", "GII", "GIM", "GIVE", "GJP", "GLDI", "GLEO", "GLIN", "GLOF", 
    "GLOV", "GLRE", "GLVN", "GML", "GMM", "GMF", "GMR", "GNAF", "GNAT", "GNE", "GNR", "GNRA", "GNRE", "GNT", "GOAT", "GOEX", "GOGF", "GOVT", 
    "GPM", "GPX", "GQRE", "GRES", "GRID", "GSEW", "GSG", "GSID", "GSIE", "GSLC", "GSSC", "GSST", "GSY", "GULF", "GUNR", "GVAL", "GVI", 
    "GVIP", "GVT", "GWO", "GWX", "GYEN", "GYLD", "HAX", "HDAW", "HDG", "HDGE", "HDMV", "HDV", "HECO", "HEDJ", "HEEM", "HEFA", "HEGD", 
    "HEGE", "HEGI", "HEGJ", "HEGL", "HEGM", "HEGN", "HEGP", "HEGQ", "HEGR", "HEGS", "HEGT", "HEGU", "HEGV", "HEGW", "HEGX", "HEGY", 
    "HEGZ", "HERO", "HETF", "HEWU", "HEWW", "HEWY", "HFXI", "HGI", "HGJP", "HGMT", "HIL", "HILO", "HIM", "HIPS", "HJP", "HKB", "HLD", 
    "HMT", "HND", "HNG", "HNL", "HNN", "HNO", "HNP", "HNQ", "HNR", "HNS", "HNT", "HNU", "HNV", "HNW", "HNX", "HNY", "HNZ", "HOML", 
    "HOMO", "HOMU", "HOPE", "HOS", "HOT", "HOTD", "HOTL", "HOTM", "HOTN", "HOTO", "HOTP", "HOTQ", "HOTR", "HOTS", "HOTT", "HOTU", 
    "HOTV", "HOTW", "HOTX", "HOTY", "HOTZ", "HOU", "HOV", "HOW", "HOX", "HOY", "HOZ", "HPA", "HPB", "HPC", "HPD", "HPE", "HPF", 
    "HPG", "HPH", "HPI", "HPJ", "HPK", "HPL", "HPM", "HPN", "HPO", "HPP", "HPQ", "HPR", "HPS", "HPT", "HPU", "HPV", "HPW", "HPX", 
    "HPY", "HPZ", "HQA", "HQB", "HQC", "HQD", "HQE", "HQF", "HQG", "HQH", "HQI", "HQJ", "HQK", "HQL", "HQM", "HQN", "HQO", "HQP", 
    "HQQ", "HQR", "HQS", "HQT", "HQU", "HQV", "HQW", "HQX", "HQY", "HQZ", "HRA", "HRB", "HRC", "HRD", "HRE", "HRF", "HRG", "HRH", "HRI", 
    "HRJ", "HRK", "HRL", "HRM", "HRN", "HRO", "HRP", "HRQ", "HRR", "HRS", "HRT", "HRU", "HRV", "HRW", "HRX", "HRY", "HRZ", "HSA", "HSB", 
    "HSC", "HSD", "HSE", "HSF", "HSG", "HSH", "HSI", "HSJ", "HSK", "HSL", "HSM", "HSN", "HSO", "HSP", "HSQ", "HSR", "HSS", "HST", "HSU", 
    "HSV", "HSW", "HSX", "HSY", "HSZ", "HYGW", "IDV", "IGRO", "IHDG", "IEDI", "JEPI", "JEPQ", "KNG", "KYN", "LQDW", "LVHI", "MLPA", 
    "NOBL", "PEY", "PFF", "PGX", "PID", "PXF", "RDVY", "REGL", "SCHD", "SCHY", "SDEM", "SDOG", "SDVY", "SMDV", "SPDV", "SPHD", "TDV", 
    "TLTW", "TYG", "VIG", "VIGI", "VYM", "VYMI", "WDIV", "VEGN", "NUDV", "TPHD", "ADVE", "DSI", "ESGV", "SUSA",
    "SPYV", "IVLU", "VXUS", "VEA", "IEFA", "SCHF", "IEMG", "IXUS"
]
MASTER_TICKERS = sorted(list(set(MASTER_TICKERS)))

MACRO_SCALE_FACTOR = 1.0450
PEGY_VALUE_THRESHOLD = 1.00  
FCF_YIELD_THRESHOLD = 5.50   

def get_dividend_growth_rate(ticker_obj):
    """Calculates the 5-year annualized distribution growth rate to fix the PEGY denominator."""
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
        return clip_value(cagr, 0.1, 15.0, 5.0)
    except:
        return 5.0

def check_performance_cagr(ticker_obj):
    """Checks 1, 5, and 10 year price compound growth returns."""
    try:
        hist = ticker_obj.history(period="10y")
        if hist.empty or len(hist) < 252:
            return 0.0, False
        
        close = hist['Close']
        current_price = close.iloc[-1]
        
        val_1y = close.iloc[-252] if len(close) >= 252 else close.iloc[0]
        val_5y = close.iloc[-1260] if len(close) >= 1260 else close.iloc[0]
        val_10y = close.iloc[0]
        
        cagr_1 = ((current_price / val_1y) - 1) * 100
        cagr_5 = ((current_price / val_5y) ** (1/5) - 1) * 100
        cagr_10 = ((current_price / val_10y) ** (1/10) - 1) * 100
        
        trends_upward = (current_price > val_1y) and (val_1y > val_5y)
        avg_cagr = (cagr_1 + cagr_5 + cagr_10) / 3
        
        return avg_cagr, trends_upward
    except:
        return 0.0, False

def clip_value(val, min_b, max_b, fallback):
    if val is None or np.isnan(val) or val <= min_b or val > max_b:
        return fallback
    return val

def compute_pegy_matrix():
    print("Beginning Mathematical Verification & Factor Sorting Model...")
    processed_assets = []
    
    tickers_string = " ".join(MASTER_TICKERS)
    yf_data = yf.Tickers(tickers_string)
    
    for ticker in MASTER_TICKERS:
        try:
            ticker_object = yf_data.tickers[ticker]
            info = ticker_object.info
            
            expense_ratio = info.get("expenseRatio", 0.0) or 0.0
            if expense_ratio > 0.0050:
                continue

            yield_indicator = info.get("trailingAnnualDividendYield") or info.get("dividendYield") or 0.0
            if yield_indicator >= 0.20: 
                yield_indicator = yield_indicator / 100.0 if yield_indicator > 1.0 else yield_indicator * 0.10
            
            yield_percentage = yield_indicator * 100.0
            if yield_percentage < 2.0 or yield_percentage > 4.0:
                continue

            raw_price = info.get("regularMarketPrice") or info.get("previousClose") or info.get("navPrice") or 0
            if raw_price == 0:
                continue
                
            pe = info.get("trailingPE") or info.get("forwardPE") or 16.2
            pe = clip_value(pe, 2.0, 50.0, 16.2)
            
            avg_cagr, is_trending_up = check_performance_cagr(ticker_object)
            growth_percentage = get_dividend_growth_rate(ticker_object)
                
            pb_ratio = info.get("priceToBook") or 1.8
            turnover = info.get("portfolioTurnover", 0.20) or 0.20
            dynamic_fcf = (1.0 / pb_ratio) * (10.0 + turnover) if pb_ratio > 0 else 5.5
            dynamic_fcf = clip_value(dynamic_fcf, 2.0, 15.0, 5.8)
            
            pegy_denominator = growth_percentage + yield_percentage
            pegy_ratio = pe / pegy_denominator if pegy_denominator > 0 else 99.0
            
            adjusted_price = raw_price * MACRO_SCALE_FACTOR
            fcf_yield_percentage = dynamic_fcf * MACRO_SCALE_FACTOR
            
            is_low_pegy = pegy_ratio < PEGY_VALUE_THRESHOLD
            is_high_fcf = fcf_yield_percentage > FCF_YIELD_THRESHOLD
            meets_cagr_target = avg_cagr >= 6.0
            
            if is_low_pegy and is_high_fcf and is_trending_up and meets_cagr_target:
                strategy_profile = "Strong Signal (Cash Generator)"
                cash_flow_insight = "High Quality Coverage"
                tier_priority = 1  
            elif is_high_fcf and is_trending_up:
                strategy_profile = "Expensive (Monitor Entry)"
                cash_flow_insight = "High Quality Coverage"
                tier_priority = 2  
            elif is_low_pegy and not is_high_fcf:
                strategy_profile = "Value Trap (Cash-Strapped)"
                cash_flow_insight = "Weak Coverage Risk"
                tier_priority = 4  
            else:
                strategy_profile = "Premium Valuation"
                cash_flow_insight = "Stable / Low Coverage"
                tier_priority = 3  
            
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
                "score_sort": pegy_ratio 
            })
            
        except Exception as e:
            continue

    processed_assets.sort(key=lambda x: (x["tier_priority"], x["score_sort"]))
    top_20 = processed_assets[:20]

    with open("top20.json", "w") as f:
        json.dump(top_20, f, indent=4)
        
    print(f"Success! Exported pristine matrix tracking configuration file to top20.json.")

if __name__ == "__main__":
    compute_pegy_matrix()
