import pandas as pd
import os

def load_data(file_name, last_mod_time):
    file_path = os.path.join("data_set", file_name)
    xls = pd.ExcelFile(file_path)
    
    def get_clean_df(sheet_name):
        if not sheet_name:
            return pd.DataFrame()
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        if '' in df.columns:
            df = df.drop(columns=[''])
        for col in df.columns:
            if col not in ['GOV_LEVEL', 'MONTH_NAME', 'BUSINESS_UNIT', 'ACCOUNT', 'QUARTER_NAME', 'EXPENDITURE_CATEGORY', 'SECTOR']:
                if df[col].dtype == 'object':
                    s = df[col].astype(str).str.strip()
                    s = s.str.replace(r'[\'"]', '', regex=True)
                    s = s.str.replace(',', '', regex=True)
                    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
                    s = s.replace('-', '0')
                    df[col] = pd.to_numeric(s, errors='coerce').fillna(0)
        return df

    # Smart sheet detection based on columns
    sheet_names = xls.sheet_names
    gov_sheet = org_sheet = econ_sheet = None
    monthly_2026 = monthly_2025 = None
    qtr_2026 = qtr_2025 = None

    for s in sheet_names:
        cols = [str(c).upper().strip() for c in pd.read_excel(xls, s, nrows=0).columns]
        if 'GOV_LEVEL' in cols and not gov_sheet:
            gov_sheet = s
        elif 'MONTH_NAME' in cols:
            if '2025' in s: monthly_2025 = s
            else: monthly_2026 = s
        elif 'QUARTER_NAME' in cols:
            if '2025' in s: qtr_2025 = s
            else: qtr_2026 = s
        elif ('SECTOR' in cols or 'BUSINESS_UNIT' in cols) and not org_sheet:
            org_sheet = s
        elif ('EXPENDITURE_CATEGORY' in cols or 'ACCOUNT' in cols) and not econ_sheet:
            econ_sheet = s

    return {
        "gov": get_clean_df(gov_sheet),
        "monthly_2026": get_clean_df(monthly_2026),
        "monthly_2025": get_clean_df(monthly_2025),
        "org": get_clean_df(org_sheet),
        "econ": get_clean_df(econ_sheet),
        "qtr_2026": get_clean_df(qtr_2026),
        "qtr_2025": get_clean_df(qtr_2025),
    }

def get_last_mod(fname):
    p = os.path.join("data_set", fname)
    return os.path.getmtime(p) if os.path.exists(p) else 0

def get_overall(df):
    row = df[df['GOV_LEVEL'].str.strip() == 'All'].iloc[0]
    return {
        "Financial Law": row.get("ORIGINAL_BUDGET", 0),
        "Modified Law": row.get("CURRENT_BUDGET", 0),
        "Implementation": row.get("IMPLEMENTATION", 0),
    }

def get_level(df, level_name):
    rows = df[df['GOV_LEVEL'].str.strip() == level_name]
    if not rows.empty:
        return rows.iloc[0].get("IMPLEMENTATION", 0), rows.iloc[0].get("CURRENT_BUDGET", 1)  # avoid div by 0
    return 0, 1
