import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.io as pio
from textwrap import dedent
import pandas as pd
import os
import json

st.set_page_config(
    page_title="FMIS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize theme session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# =========================
# Helpers
# =========================
def html(block: str):
    st.markdown(dedent(block).strip(), unsafe_allow_html=True)


def format_money(value: float) -> str:
    return f"{value:,.0f} KHR"


def format_summary(value: float) -> str:
    return f"{value:,.0f} KHR"


def format_exact(value: float) -> str:
    return f"{value:,.0f} KHR"


# =========================
# Styling
# =========================
is_light = st.session_state.theme == 'light'

# Define theme colors based on state
theme_vars = {
    "bg": "#FAF9F6" if is_light else "#04122b",
    "panel": "#FAF9F6" if is_light else "#1a2d4a",
    "card": "#FAF9F6" if is_light else "#374d6c",
    "text": "#1e293b" if is_light else "#e9f2ff",
    "cyan": "#3498dc" if is_light else "#20d6ff",
    "blue": "#3498dc" if is_light else "#00A8E1",
    "green": "#1abc9c" if is_light else "#00AD4E",
    "border": "#94a3b8" if is_light else "rgba(92, 132, 184, 0.6)",
    "kpi_bg": "#FAF9F6" if is_light else "linear-gradient(135deg, rgba(58, 77, 108, 0.95), rgba(26, 45, 74, 0.95))",
    "shadow": "none",
    "app_bg": "#FAF9F6" if is_light else "linear-gradient(180deg, #020c1c 0%, #061731 100%)",
    "chart_bg": "#FAF9F6" if is_light else "linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4))",
}

html(
    f'''
    <style>
        :root {{
            --bg: {theme_vars["bg"]};
            --panel: {theme_vars["panel"]};
            --card: {theme_vars["card"]};
            --text: {theme_vars["text"]};
            --cyan: {theme_vars["cyan"]};
            --blue: {theme_vars["blue"]};
            --teal: #08c6df;
            --green: {theme_vars["green"]};
            --orange: #ff9300;
            --red: #ff5a5a;
            --border: {theme_vars["border"]};
            --kpi-bg: {theme_vars["kpi_bg"]};
            --shadow: {theme_vars["shadow"]};
            --app-bg: {theme_vars["app_bg"]};
            --chart-bg: {theme_vars["chart_bg"]};
        }}

        header[data-testid="stHeader"] {{ display: none !important; height: 0 !important; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        .stAppToolbar {{ display: none !important; }}
        #MainMenu {{ visibility: hidden !important; }}
        footer {{ visibility: hidden !important; }}

        .stApp {{
            background: var(--app-bg) !important;
            color: var(--text) !important;
        }}

        .block-container {{
            max-width: 1920px;
            padding-top: 0.1rem !important;
            padding-bottom: 0.1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }}

        div[data-testid="stHorizontalBlock"] {{
            gap: 0.6rem;
        }}

        div[data-testid="column"] {{
            padding: 0 !important;
        }}

        /* Streamlit Button Styling */
        button[kind="secondary"] {{
            background-color: var(--panel) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            font-weight: 600 !important;
        }}
        button[kind="secondary"]:hover {{
            border-color: var(--cyan) !important;
            color: var(--cyan) !important;
        }}

        /* Header */
        .dashboard-title {{
            text-align: left;
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--text);
            line-height: 1.1;
            margin: 0 0 0.1rem 0;
            padding-left: 0.2rem;
            animation: fadeInDown 0.8s ease-out;
        }}

        .dashboard-subtitle {{
            text-align: left;
            font-size: 0.8rem;
            color: var(--cyan);
            margin-bottom: 0.2rem;
            padding-left: 0.2rem;
            animation: fadeInDown 1s ease-out;
        }}

        /* KPI Cards */
        .kpi-card {{
            background: var(--kpi-bg);
            border-radius: 12px;
            padding: 0.8rem 1rem;
            text-align: center;
            height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border: 1.5px solid var(--border);
            box-shadow: none;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out backwards;
        }}

        .kpi-card:hover {{
            transform: translateY(-8px) scale(1.02);
            border-color: var(--cyan);
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 4px;
            background: linear-gradient(90deg, #20d6ff, #1f6bff);
        }}
        
        .kpi-card.expense::before {{
            background: linear-gradient(90deg, #00A8E1, #33B9E7);
        }}
        .kpi-card.revenue::before {{
            background: linear-gradient(90deg, #00AD4E, #14C85D);
        }}

        .kpi-label {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--cyan);
            margin-bottom: 0.6rem;
            letter-spacing: 0.5px;
        }}
        .kpi-card.expense .kpi-label {{ color: var(--blue); }}
        .kpi-card.revenue .kpi-label {{ color: var(--green); }}

        .kpi-value {{
            font-size: 1.5rem;
            font-weight: 900;
            line-height: 1;
            color: var(--text);
            margin-bottom: 0.2rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* Animations */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .anim-delay-1 {{ animation-delay: 0.1s; }}
        .anim-delay-2 {{ animation-delay: 0.2s; }}
        .anim-delay-3 {{ animation-delay: 0.3s; }}
        .anim-delay-4 {{ animation-delay: 0.4s; }}

        /* Progress Process bar */
        .process-container {{
            background: var(--panel);
            border-radius: 12px;
            padding: 1rem;
            border: 1.5px solid var(--border);
            height: 360px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.8s ease-out backwards;
            animation-delay: 0.5s;
        }}
        
        .process-title {{
            color: var(--cyan);
            font-size: 1.1rem;
            font-weight: 800;
            margin-bottom: 1.2rem;
            text-align: center;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}

        .process-row {{
            margin-bottom: 1.2rem;
        }}

        .process-label-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.4rem;
          }}

        .process-track {{
            width: 100%;
            height: 12px;
            border-radius: 999px;
            background: rgba(0, 0, 0, 0.2) !important;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.4) !important;
        }}

        .process-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--blue), var(--cyan));
            position: relative;
            animation: fillBar 2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            transform-origin: left;
        }}
        
        .process-fill::after {{
            content: '';
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shine 3s infinite linear;
        }}

        @keyframes fillBar {{
            from {{ transform: scaleX(0); }}
            to {{ transform: scaleX(1); }}
        }}
        
        @keyframes shine {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}

        /* Plotly charts styling */
        div[data-testid="stPlotlyChart"], .am-chart-container {{ 
            margin-top: 0 !important;
            margin-bottom: 0.5rem;
            border-radius: 12px;
            border: 1.5px solid var(--border);
            overflow: hidden;
            box-shadow: none;
            background: var(--chart-bg);
            transition: all 0.3s ease;
            animation: fadeInUp 0.8s ease-out backwards;
        }}
        
        div[data-testid="stPlotlyChart"]:hover, .am-chart-container:hover {{
            border-color: var(--cyan);
            box-shadow: 0 10px 20px rgba(32, 214, 255, 0.15);
        }}

        /* Slow Glow Sweep for idle movement */
        .glow-sweep-canvas {{
            position: relative;
            overflow: hidden;
        }}
        .glow-sweep-canvas::after {{
            content: '';
            position: absolute;
            top: 0; left: -150%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(32, 214, 255, 0.1), transparent);
            transform: skewX(-20deg);
            animation: globalSweep 25s infinite linear;
            pointer-events: none;
            z-index: 5;
        }}
        @keyframes globalSweep {{
            0% {{ left: -150%; }}
            10% {{ left: 150%; }}
            100% {{ left: 150%; }}
        }}

        /* Ratio Cards */
        .ratio-card {{
            background: var(--panel);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 0.5rem;
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-around;
            animation: fadeInUp 0.8s ease-out backwards;
            animation-delay: 0.4s;
        }}

        .footer-note {{
            color: var(--text) !important;
            font-size: 0.8rem;
            opacity: 0.8;
        }}

        @keyframes livePulse {{
            0% {{ opacity: 0.4; box-shadow: 0 0 0px var(--green); }}
            50% {{ opacity: 1; box-shadow: 0 0 12px var(--green); }}
            100% {{ opacity: 0.4; box-shadow: 0 0 0px var(--green); }}
        }}

        path[fill-opacity="0.155"], path[fill-opacity="0.255"], path[fill-opacity="0.455"],
        path[style*="fill-opacity: 0.155"], path[style*="fill-opacity: 0.255"], path[style*="fill-opacity: 0.455"] {{
            animation: trendPulse 3s infinite ease-in-out !important;
        }}

        @keyframes trendPulse {{
            0%   {{ opacity: 0.4; filter: brightness(1) drop-shadow(0 0 0px {theme_vars["cyan"]}); }}
            50%  {{ opacity: 1.0; filter: brightness(1.6) drop-shadow(0 0 12px {theme_vars["cyan"]}); }}
            100% {{ opacity: 0.4; filter: brightness(1) drop-shadow(0 0 0px {theme_vars["cyan"]}); }}
        }}
    </style>
    '''
)

# =========================
# Data Loading & Processing
# =========================
# Removed cache temporary to ensure live updates
def load_data(file_name, last_mod_time):
    file_path = os.path.join("data_set", file_name)
    xls = pd.ExcelFile(file_path)
    
    def get_clean_sheet(sheet_name_hint):
        sheet = [s for s in xls.sheet_names if sheet_name_hint in s][0]
        df = pd.read_excel(xls, sheet_name=sheet)
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

    return {
        "gov": get_clean_sheet("Sheet 1"),
        "monthly": get_clean_sheet("Sheet 2"),
        "org": get_clean_sheet("Sheet 3"),
        "econ": get_clean_sheet("Sheet 4"),
        "qtr": get_clean_sheet("Sheet 5"),
    }

def get_last_mod(fname):
    p = os.path.join("data_set", fname)
    return os.path.getmtime(p) if os.path.exists(p) else 0

exp_last_mod = get_last_mod("expense.xlsx")
rev_last_mod = get_last_mod("revenue.xlsx")

exp_data = load_data("expense.xlsx", exp_last_mod)
rev_data = load_data("revenue.xlsx", rev_last_mod)

def get_overall(df):
    row = df[df['GOV_LEVEL'].str.strip() == 'All'].iloc[0]
    return {
        "Financial Law": row.get("ORIGINAL_BUDGET", 0),
        "Modified Law": row.get("CURRENT_BUDGET", 0),
        "Implementation": row.get("IMPLEMENTATION", 0),
    }

exp_summary = get_overall(exp_data["gov"])
rev_summary = get_overall(rev_data["gov"])

def get_level(df, level_name):
    rows = df[df['GOV_LEVEL'].str.strip() == level_name]
    if not rows.empty:
        return rows.iloc[0].get("IMPLEMENTATION", 0), rows.iloc[0].get("CURRENT_BUDGET", 1)  # avoid div by 0
    return 0, 1

exp_nat_impl, exp_nat_mod = get_level(exp_data["gov"], "National")
exp_sub_impl, exp_sub_mod = get_level(exp_data["gov"], "Sub-national")
rev_nat_impl, rev_nat_mod = get_level(rev_data["gov"], "National")
rev_sub_impl, rev_sub_mod = get_level(rev_data["gov"], "Sub-national")

# =========================
# Render functions
# =========================

def render_kpi(col, title, value, type_class, delay_class):
    with col:
        html(
            f'''
            <div class='kpi-card {type_class} {delay_class}' title='{format_exact(value)}'>
                <div class='kpi-label'>{title}</div>
                <div class='kpi-value' style='font-size: 1.5rem;'>{format_summary(value)}</div>
            </div>
            '''
        )

def render_ratio(col, title, impl, mod, type_class):
    ratio = (impl / mod) * 100 if mod > 0 else 0
    display_ratio = min(ratio, 100)
    
    color = "#00A8E1" if type_class == 'expense' else "#00AD4E"
    
    is_dark = st.session_state.theme == 'dark'
    text_color = "white" if is_dark else "#1e293b"
    title_color = "#a0c4ff" if is_dark else "#475569"
    
    with col:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = ratio,
            number = {"suffix": "%", "font": {"size": 32, "color": text_color, "family": "Arial Black"}},
            title = {"text": f"<b>{title}</b>", "font": {"size": 14, "color": title_color, "family": "Arial"}},
            domain = {'y': [0.15, 1], 'x': [0, 1]},
            gauge = {
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "gray", "ticklen": 5},
                "bar": {"color": color, "thickness": 0.45},
                "bgcolor": "rgba(128,128,128,0.25)",
                "borderwidth": 0,
                "threshold": {
                    "line": {"color": "white" if is_dark else "#1e293b", "width": 4},
                    "thickness": 0.75,
                    "value": ratio
                }
            }
        ))
        
        fig.update_layout(
            height=235,
            margin=dict(l=35, r=35, t=55, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': text_color, 'family': "Arial"},
            annotations=[
                {
                    "text": "Implementation / Modified Law",
                    "x": 0.5, "y": 0.02,
                    "xref": "paper", "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 10, "color": "#789bc7", "family": "Arial"}
                }
            ]
        )
        
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_process_row(label, value, target, is_expense=True, custom_gradient=None):
    pct = (value / target * 100) if target > 0 else 0
    display_pct = min(pct, 100)
    
    # Default light-themed gradients if none provided
    if not custom_gradient:
        color = "linear-gradient(90deg, #00A8E1, #33B9E7)" if is_expense else "linear-gradient(90deg, #00AD4E, #14C85D)"
    else:
        color = custom_gradient
        
    is_dark = st.session_state.theme == 'dark'
    text_color = "#edf6ff" if is_dark else "#1e293b"
    # For Light Mode, we use slightly darker blue/green for readability on white
    label_color = ("#67ebff" if is_dark else "#0284c7") if is_expense else ("#8affc2" if is_dark else "#059669")
    secondary_text = "#789bc7" if is_dark else "#475569"
    glow = "rgba(0, 168, 225, 0.3)" if is_expense else "rgba(0, 173, 78, 0.3)"
    
    return "".join([
        "<div class='process-row' style='margin-bottom: 0.1rem;'>",
        # Level Label (Header)
        f"<div style='font-size: 0.85rem; font-weight: 600; color: {text_color}; margin-bottom: 0px;'>{label}</div>",
        # Progress Bar
        "<div class='process-track' style='height: 10px; margin-bottom: 1px;'>",
        f"<div class='process-fill' style='width:{display_pct}%; background:{color}; box-shadow: 0 0 5px {glow}; border-radius: 4px;'></div>",
        "</div>",
        # Data Row (Footer)
        "<div style='display: flex; justify-content: space-between; align-items: baseline;'>",
        # LEFT: Implementation
        "<div>",
        f"<span style='color:{label_color}; font-size: 0.95rem; font-weight: 800;'>{format_money(value)}</span> ",
        f"<span style='color:{label_color}; font-size: 0.75rem; font-weight: 500; opacity: 0.9;'>({pct:.1f}%)</span>",
        "</div>",
        # RIGHT: Modified Law
        "<div style='text-align: right;'>",
        f"<span style='font-size: 0.6rem; color: #5c84b8; text-transform: uppercase; letter-spacing: 0.8px; margin-right: 4px;'>Modified Law</span>",
        f"<span style='font-size: 0.8rem; color: {secondary_text}; font-weight: 700;'>{format_money(target)}</span>",
        "</div>",
        "</div>",
        "</div>"
    ])

def render_process_bar():
    exp_body = ""
    # Each bar gets a unique distinct light gradient
    exp_body += render_process_row("National Level", exp_nat_impl, exp_nat_mod, is_expense=True, 
                                   custom_gradient="linear-gradient(90deg, #00A8E1, #33B9E7)")
    exp_body += render_process_row("Sub-National Level", exp_sub_impl, exp_sub_mod, is_expense=True,
                                   custom_gradient="linear-gradient(90deg, #1f6bff, #67ebff)")
    
    rev_body = ""
    # Each bar gets a unique distinct light gradient
    rev_body += render_process_row("National Level", rev_nat_impl, rev_nat_mod, is_expense=False,
                                   custom_gradient="linear-gradient(90deg, #00AD4E, #14C85D)")
    rev_body += render_process_row("Sub-National Level", rev_sub_impl, rev_sub_mod, is_expense=False,
                                   custom_gradient="linear-gradient(90deg, #20d6a2, #8affc2)")
    
    is_dark = st.session_state.theme == 'dark'
    title_color_exp = "#67ebff" if is_dark else "#0284c7"
    title_color_rev = "#8affc2" if is_dark else "#059669"

    html(
        f'''
        <div class="process-container">
            <div style="width: 100%;">
                <div class="process-title" style="color: {title_color_exp}; margin-bottom: 0.4rem;">Expense Implementation</div>
                {exp_body}
            </div>
            <div style="width: 100%;">
                <div class="process-title" style="color: {title_color_rev}; margin-bottom: 0.4rem; margin-top: 0.2rem;">Revenue Implementation</div>
                {rev_body}
            </div>
        </div>
        '''
    )
def render_top5_gauge_chart(df, title, is_expense=True):
    # Sort and take top 5
    df_sorted = df.sort_values(by="IMPLEMENTATION", ascending=False).head(5)
    
    # Theme Colors: Expense = Reds, Revenue = Greens
    if is_expense:
        # High-impact Blues (Prime Video Style)
        color_palette = ['#00A8E1', '#1A7BB8', '#33B9E7', '#66CBED', '#a0c4ff']
    else:
        # High-impact Greens (Smart 5G Style)
        color_palette = ['#00AD4E', '#11ba7a', '#20d6a2', '#4adeb5', '#8affc2']
    
    chart_data = []
    for i, row in enumerate(df_sorted.itertuples()):
        impl = float(getattr(row, "IMPLEMENTATION", 0))
        target = float(getattr(row, "MODIFIED_LAW", getattr(row, "CURRENT_BUDGET", 1)))
        pct = (impl / target * 100) if target > 0 else 0
        label_val = getattr(row, "EXPENDITURE_CATEGORY", getattr(row, "ACCOUNT", "Unknown"))
        label = str(label_val)
        
        
        chart_data.append({
            "category": label,
            "value": round(float(pct), 1),
            "impl": f"{impl:,.0f} KHR",
            "target": f"{target:,.0f} KHR",
            "full": 100,
            "columnSettings": { "fill": color_palette[i % len(color_palette)] }
        })

    # amCharts radar order: first is inside, last is outside.
    chart_data.reverse()
    chart_json = json.dumps(chart_data)
    
    # Unique ID for each gauge instance
    import random
    import string
    uid = ''.join(random.choices(string.ascii_lowercase, k=4))
    chart_uid = f"gauge_{uid}"

    is_dark = st.session_state.theme == 'dark'
    bg_style = "background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));" if is_dark else "background: #FAF9F6;"
    title_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#789bc7" if is_dark else "#64748b"
    track_color = "0x1a2d4a" if is_dark else "0xcccccc"
    tooltip_bg = "0x04122b" if is_dark else "0xFAF9F6"
    tooltip_stroke = "0x5c84b8" if is_dark else "0x3498dc"
    text_color_hex = "0xffffff" if is_dark else "0x1e293b"
    label_color_hex = "0x789bc7" if is_dark else "0x475569"

    border_color = "rgba(92, 132, 184, 0.6)" if is_dark else "#94a3b8"
    shadow_val = "0 8px 16px rgba(0,0,0,0.2)" if is_dark else "0 4px 12px rgba(0, 0, 0, 0.12)"

    amcharts_html = f"""
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; }}
    </style>
    <div id="container_{chart_uid}" class="am-chart-container glow-sweep-canvas" style="
        height: 240px;
        box-sizing: border-box;
        border-radius: 12px;
        border: 1.5px solid {border_color};
        overflow: hidden;
        box-shadow: none;
        {bg_style}
        padding: 20px 22px;
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: border-color 0.3s ease;
        font-family: sans-serif;
    ">
        <!-- Dashboard-consistent Title -->
        <div style="width: 100%; color: {title_color}; font-size: 14px; font-weight: bold; margin-bottom: 18px; text-align: left; font-family: Arial, sans-serif;">
            {title}
        </div>
        
        <!-- The Gauge -->
        <div id="{chart_uid}" style="width: 100%; height: 190px;" class="glow-sweep-canvas"></div>
    </div>
    
    <script src="https://cdn.amcharts.com/lib/5/index.js"></script>
    <script src="https://cdn.amcharts.com/lib/5/xy.js"></script>
    <script src="https://cdn.amcharts.com/lib/5/radar.js"></script>
    <script src="https://cdn.amcharts.com/lib/5/themes/Animated.js"></script>

    <script>
    am5.ready(function() {{
        var root = am5.Root.new("{chart_uid}");

        root.setThemes([am5themes_Animated.new(root)]);
        root.interfaceColors.set("fontFamily", "Arial, sans-serif");

        var chart = root.container.children.push(am5radar.RadarChart.new(root, {{
          panX: false, panY: false, wheelX: "none", wheelY: "none",
          paddingTop: 0, paddingBottom: 0, paddingLeft: 0, paddingRight: 0,
          innerRadius: am5.percent(20),
          startAngle: -90,
          endAngle: 180
        }}));

        var data = {chart_json};

        // Angular Axis (0-100%)
        var xRenderer = am5radar.AxisRendererCircular.new(root, {{
          strokeOpacity: 0.1,
          minGridDistance: 50
        }});
        xRenderer.labels.template.setAll({{ 
          radius: 10, 
          fill: am5.color({label_color_hex}), 
          fontSize: 10, 
          fontWeight: "normal",
          fontFamily: "Arial, sans-serif"
        }});
        xRenderer.grid.template.setAll({{ strokeOpacity: 0.05 }});

        var xAxis = chart.xAxes.push(am5xy.ValueAxis.new(root, {{
          renderer: xRenderer, min: 0, max: 100,
          strictMinMax: true, numberFormat: "#'%'",
        }}));

        // Radial Axis (Categories)
        var yRenderer = am5radar.AxisRendererRadial.new(root, {{ 
            minGridDistance: 1 
        }});
        
        yRenderer.labels.template.setAll({{
          centerX: am5.p100,
          fontWeight: "normal",
          fontSize: 10,
          fill: am5.color({text_color_hex}),
          paddingRight: 12,
          fontFamily: "Arial, sans-serif"
        }});
        
        yRenderer.grid.template.setAll({{ forceHidden: true }});

        var yAxis = chart.yAxes.push(am5xy.CategoryAxis.new(root, {{
          categoryField: "category",
          renderer: yRenderer
        }}));
        yAxis.data.setAll(data);

        // Tracks (The shadow rings - Theme Consistent Dark)
        var series1 = chart.series.push(am5radar.RadarColumnSeries.new(root, {{
          xAxis: xAxis, yAxis: yAxis, clustered: false,
          valueXField: "full", categoryYField: "category",
          fill: am5.color({track_color}), fillOpacity: 0.5
        }}));
        series1.columns.template.setAll({{ width: am5.percent(70), strokeOpacity: 0, cornerRadius: 20 }});
        series1.data.setAll(data);

        // Tooltip Styling
        var tooltip = am5.Tooltip.new(root, {{
          getFillFromSprite: false,
          labelText: "[bold]{{category}}[/]\\nImplementation: {{impl}}\\nModified Law: {{target}}\\nRatio: {{valueX}}%"
        }});
        
        // Ensure tooltip text is visible in both modes
        tooltip.label.setAll({{ 
          fill: am5.color({text_color_hex}),
          fontSize: 12
        }});

        tooltip.get("background").setAll({{
          fill: am5.color({tooltip_bg}),
          fillOpacity: 0.95,
          stroke: am5.color({tooltip_stroke}),
          strokeWidth: 2,
          strokeOpacity: 0.3
        }});


        // Value Rings
        var series2 = chart.series.push(am5radar.RadarColumnSeries.new(root, {{
          xAxis: xAxis, yAxis: yAxis, clustered: false,
          valueXField: "value", categoryYField: "category",
          sequencedInterpolation: true,
          sequencedDelay: 200
        }}));
        
        series2.columns.template.setAll({{
          width: am5.percent(70), strokeOpacity: 0,
          cornerRadius: 20,
          templateField: "columnSettings",
          tooltipText: "[bold]{{category}}[/]\\nImplementation: {{impl}}\\nModified Law: {{target}}\\nRatio: {{valueX}}%",
          tooltip: tooltip
        }});

        series2.data.setAll(data);

        series2.data.setAll(data);

        series1.appear(1500, 100);
        series2.appear(1500, 200);
        chart.appear(1500, 100);
        if(root._logo) {{ root._logo.dispose(); }}
    }}); 
    </script>
    """
    components.html(amcharts_html, height=240)

def render_top5_chart(df, title, is_expense=True):
    # Only consider positive contributions for Top 5
    df = df[df["IMPLEMENTATION"] > 0].copy()
    df_sorted = df.sort_values(by="IMPLEMENTATION", ascending=True).tail(5)
    
    # Handle dynamic label column names
    label_col = "EXPENDITURE_CATEGORY" if "EXPENDITURE_CATEGORY" in df.columns else "ACCOUNT"
    categories = df_sorted[label_col].astype(str).tolist()
    values = df_sorted["IMPLEMENTATION"].tolist()
    
    # Use gradients for bars to make them "fancy"
    base_color = '#00A8E1' if is_expense else '#00AD4E'
    
    max_val = max(values) if values else 1
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=categories, x=values, orientation='h',
        marker={"color": base_color, "line": {"color": 'rgba(255,255,255,0.2)', "width": 1}},
        text=[f"{v:,.0f} KHR" for v in values],
        textposition='outside',
        cliponaxis=False,
        hovertemplate='<b>%{y}</b><br>Amount: %{x:,.0f} KHR<extra></extra>'
    ))
    
    is_dark = st.session_state.theme == 'dark'
    text_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b" # Light black
    data_label_color = "white" if is_dark else "#1e293b"
    grid_color = "rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.05)"

    fig.update_traces(textfont_color=data_label_color)

    fig.update_layout(
        title={"text": title, "font": {"size": 13, "color": text_color, "family": "sans-serif"}},
        height=300,
        margin={"l": 45, "r": 0, "t": 40, "b": 10}, 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 11},
        xaxis={
            "showline": False, 
            "showgrid": True, 
            "gridcolor": grid_color, 
            "ticksuffix": " KHR", 
            "tickformat": ".0s",
            "range": [0, max_val * 1.8],
            "tickfont": {"color": label_color}
        },
        yaxis={
            "showline": False, 
            "showgrid": False, 
            "type": "category",
            "tickfont": {"color": label_color}
        },
        showlegend=False,
        transition={'duration': 1000, 'easing': 'cubic-in-out'}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_top5_funnel_chart(df, title, is_expense=True, margin_left=80):
    df_sorted = df.sort_values(by="IMPLEMENTATION", ascending=False).head(5)
    # Handle dynamic label column names
    label_col = "SECTOR" if "SECTOR" in df.columns else "BUSINESS_UNIT"
    import textwrap
    # Tighter wrapping to save horizontal space
    labels = [textwrap.fill(str(l), width=18).replace('\n', '<br>') for l in df_sorted[label_col]]
    values = df_sorted["IMPLEMENTATION"].tolist()
    
    formatted_text = [f"{v:,.0f} KHR" for v in values]

    if is_expense:
        colors = ['#00A8E1', '#1A7BB8', '#33B9E7', '#66CBED', '#a0c4ff']
        connector_color = "rgba(0, 168, 225, 0.15)"
    else:
        colors = ['#00AD4E', '#11ba7a', '#20d6a2', '#4adeb5', '#8affc2']
        connector_color = "rgba(0, 173, 78, 0.15)"
        
    fig = go.Figure(go.Funnel(
        y=labels,
        x=values,
        text=formatted_text,
        textinfo="text",
        textposition="auto",
        textfont={"color": '#ffffff' if st.session_state.theme == 'dark' else '#1e293b', "size": 10, "family": "Arial"},
        marker={"color": colors, "line": {"width": 1, "color": "rgba(255,255,255,0.2)"}},
        connector={
            "fillcolor": connector_color,
            "line": {"color": "rgba(255, 255, 255, 0.15)", "width": 1}
        },
        hovertemplate='<b>%{y}</b><br>Amount: %{x:,.0f} KHR<extra></extra>'
    ))
    
    is_dark = st.session_state.theme == 'dark'
    bg_style = "background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));" if is_dark else "background: #FAF9F6;"
    title_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b" 
    border_color = "rgba(92, 132, 184, 0.6)" if is_dark else "#94a3b8"
    shadow_val = "none"

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": title_color, "family": "Arial"}, "x": 0.05, "y": 0.92},
        height=240, 
        margin={"l": margin_left + 15, "r": 30, "t": 60, "b": 15}, 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 10},
        showlegend=False,
        transition={'duration': 1200, 'easing': 'cubic-in-out'}
    )
    
    fig.update_xaxes(visible=False)
    fig.update_yaxes(
        type='category',
        showgrid=False, 
        zeroline=False, 
        tickfont={"size": 11, "color": label_color}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_combined_monthly_chart(df_exp, df_rev, title):
    # Standard month order for sorting
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Merge dataframes
    df_merged = pd.merge(df_exp, df_rev, on="MONTH_NAME", suffixes=("_EXP", "_REV"), how="outer")
    
    # Ensure standard sorting by month
    # We map the month names to their index in the order list for robust sorting
    month_map = {m: i for i, m in enumerate(month_order)}
    df_merged['MONTH_IDX'] = df_merged['MONTH_NAME'].str.strip().str[:3].str.title().map(month_map)
    df_merged = df_merged.sort_values('MONTH_IDX').dropna(subset=['MONTH_IDX'])
    
    months = df_merged["MONTH_NAME"].astype(str).tolist()
    exp_values = df_merged["IMPLEMENTATION_EXP"].fillna(0).tolist()
    rev_values = df_merged["IMPLEMENTATION_REV"].fillna(0).tolist()
    
    fig = go.Figure()
    
    # Base traces
    fig.add_trace(go.Scatter(
        x=months, y=rev_values, name='Revenue', mode='markers+lines',
        line={"color": '#00AD4E', "width": 3, "shape": "spline", "smoothing": 1}, 
        marker={"size": 8, "color": "#ffffff", "line": {"width": 2, "color": '#00AD4E'}},
        fill='tozeroy', fillcolor='rgba(0, 173, 78, 0.10)',
        hovertemplate='<b>%{x}</b><br>Revenue: %{y:,.0f} KHR<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=months, y=exp_values, name='Expense', mode='markers+lines',
        line={"color": '#00A8E1', "width": 3, "shape": "spline", "smoothing": 1}, 
        marker={"size": 8, "color": "#ffffff", "line": {"width": 2, "color": '#00A8E1'}},
        fill='tozeroy', fillcolor='rgba(0, 168, 225, 0.10)',
        hovertemplate='<b>%{x}</b><br>Expense: %{y:,.0f} KHR<extra></extra>'
    ))

    is_dark = st.session_state.theme == 'dark'
    text_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b" # Light black
    grid_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
    annot_bg = "rgba(4, 18, 43, 0.8)" if is_dark else "rgba(255, 255, 255, 0.9)"
    annot_text_rev = "#00AD4E" if is_dark else "#059669" # Slightly darker green for light mode
    annot_text_exp = "#00A8E1" if is_dark else "#0284c7" # Slightly darker blue for light mode

    # Identify and Highlight Peak and Valley
    if rev_values:
        r_max_idx = rev_values.index(max(rev_values))
        r_min_idx = rev_values.index(min(rev_values))
        
        # Max Revenue Annotation
        fig.add_annotation(
            x=months[r_max_idx], y=rev_values[r_max_idx],
            text="Highest Rev", showarrow=True, arrowhead=2, arrowcolor=annot_text_rev,
            ax=0, ay=-40, font={"color": annot_text_rev, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_rev, borderwidth=1
        )
        # Min Revenue Annotation
        fig.add_annotation(
            x=months[r_min_idx], y=rev_values[r_min_idx],
            text="Lowest Rev", showarrow=True, arrowhead=2, arrowcolor=annot_text_rev,
            ax=0, ay=40, font={"color": annot_text_rev, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_rev, borderwidth=1
        )
        
        # Add a "Glow" effect for Max/Min Revenue (3-Layer Animated)
        # Layer 1: Outer Pulse
        fig.add_trace(go.Scatter(
            x=[months[r_max_idx], months[r_min_idx]], y=[rev_values[r_max_idx], rev_values[r_min_idx]], 
            mode='markers',
            marker={"size": 22, "color": "rgba(0, 173, 78, 0.155)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        # Layer 2: Middle Pulse
        fig.add_trace(go.Scatter(
            x=[months[r_max_idx], months[r_min_idx]], y=[rev_values[r_max_idx], rev_values[r_min_idx]], 
            mode='markers',
            marker={"size": 15, "color": "rgba(0, 173, 78, 0.255)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        # Layer 3: Solid Beacon
        fig.add_trace(go.Scatter(
            x=[months[r_max_idx], months[r_min_idx]], y=[rev_values[r_max_idx], rev_values[r_min_idx]], 
            mode='markers',
            marker={"size": 9, "color": "rgba(0, 173, 78, 0.455)", "line": {"color": "#00AD4E", "width": 2}},
            showlegend=False, hoverinfo='skip'
        ))

    if exp_values:
        e_max_idx = exp_values.index(max(exp_values))
        e_min_idx = exp_values.index(min(exp_values))

        # Max Expense Annotation
        fig.add_annotation(
            x=months[e_max_idx], y=exp_values[e_max_idx],
            text="Highest Exp", showarrow=True, arrowhead=2, arrowcolor=annot_text_exp,
            ax=0, ay=-40, font={"color": annot_text_exp, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_exp, borderwidth=1
        )
        # Min Expense Annotation
        fig.add_annotation(
            x=months[e_min_idx], y=exp_values[e_min_idx],
            text="Lowest Exp", showarrow=True, arrowhead=2, arrowcolor=annot_text_exp,
            ax=0, ay=40, font={"color": annot_text_exp, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_exp, borderwidth=1
        )
        
        # Add a "Glow" effect for Max/Min Expense (3-Layer Animated)
        # Layer 1: Outer Pulse
        fig.add_trace(go.Scatter(
            x=[months[e_max_idx], months[e_min_idx]], y=[exp_values[e_max_idx], exp_values[e_min_idx]], 
            mode='markers',
            marker={"size": 22, "color": "rgba(0, 168, 225, 0.155)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        # Layer 2: Middle Pulse
        fig.add_trace(go.Scatter(
            x=[months[e_max_idx], months[e_min_idx]], y=[exp_values[e_max_idx], exp_values[e_min_idx]], 
            mode='markers',
            marker={"size": 15, "color": "rgba(0, 168, 225, 0.255)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        # Layer 3: Solid Beacon
        fig.add_trace(go.Scatter(
            x=[months[e_max_idx], months[e_min_idx]], y=[exp_values[e_max_idx], exp_values[e_min_idx]], 
            mode='markers',
            marker={"size": 9, "color": "rgba(0, 168, 225, 0.455)", "line": {"color": "#00A8E1", "width": 2}},
            showlegend=False, hoverinfo='skip'
        ))

    # Identifiers for Peak and Valley are already added. Use the variables defined at the top.
    
    # Final Layout Polish
    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": text_color, "family": "Arial"}},
        height=255,
        margin={"l": 20, "r": 20, "t": 40, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 11},
        xaxis={
            "showline": False, 
            "showgrid": False, 
            "type": "category",
            "tickfont": {"color": label_color}
        },
        yaxis={
            "showline": False, 
            "showgrid": True, 
            "gridcolor": grid_color, 
            "ticksuffix": " KHR", 
            "tickformat": ".0s",
            "tickfont": {"color": label_color}
        },
        showlegend=True,
        legend={
            "orientation": "h", 
            "yanchor": "bottom", 
            "y": 1.02, 
            "xanchor": "right", 
            "x": 1,
            "font": {"color": label_color}
        },
        hovermode="x unified",
        transition={"duration": 1000, "easing": "cubic-in-out"}
    )
    
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_quarterly_chart(df_exp, df_rev, title):
    df_merged = pd.merge(df_exp, df_rev, on="QUARTER_NAME", suffixes=("_EXP", "_REV"), how="outer")
    qtrs = df_merged["QUARTER_NAME"].astype(str).tolist()
    exp_vals = df_merged["IMPLEMENTATION_EXP"].fillna(0).tolist()
    rev_vals = df_merged["IMPLEMENTATION_REV"].fillna(0).tolist()
    
    neg_exp_vals = [(-1.0) * float(v) for v in exp_vals]
    rev_text = [f"{v:,.0f} KHR" for v in rev_vals]
    exp_text = [f"{v:,.0f} KHR" for v in exp_vals]
    
    is_dark = st.session_state.theme == 'dark'
    bar_text_color_exp = '#67ebff' if is_dark else '#1e293b'
    bar_text_color_rev = '#8affc2' if is_dark else '#1e293b'

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=qtrs, x=neg_exp_vals, orientation='h', name='Expense',
        marker={"color": '#00A8E1', "line": {"color": 'rgba(255,255,255,0.1)', "width": 1}},
        text=exp_text, textposition='outside', 
        cliponaxis=False,
        textfont={"color": bar_text_color_exp},
        hovertemplate='<b>%{y}</b><br>Expense: %{customdata:,.0f} KHR<extra></extra>',
        customdata=exp_vals
    ))
    fig.add_trace(go.Bar(
        y=qtrs, x=rev_vals, orientation='h', name='Revenue',
        marker={"color": '#00AD4E', "line": {"color": 'rgba(255,255,255,0.1)', "width": 1}},
        text=rev_text, textposition='outside', 
        cliponaxis=False,
        textfont={"color": bar_text_color_rev},
        hovertemplate='<b>%{y}</b><br>Revenue: %{x:,.0f} KHR<extra></extra>'
    ))
    
    is_dark = st.session_state.theme == 'dark'
    text_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b" # Light black
    grid_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
    center_bg = "rgba(4, 18, 43, 1.0)" if is_dark else "rgba(255, 255, 255, 0.9)"
    center_border = "rgba(32, 214, 255, 0.4)" if is_dark else "#e0e0e0"
    center_text = "#FFFFFF" if is_dark else "#1e293b"

    # Add Center Labels (Q1, Q2, etc.)
    for q in qtrs:
        fig.add_annotation(
            x=0, y=q,
            text=q,
            showarrow=False,
            font={"color": center_text, "size": 13},
            bgcolor=center_bg,
            bordercolor=center_border,
            borderwidth=1,
            borderpad=5,
            opacity=1.0
        )
    
    max_val = max(max(rev_vals) if rev_vals else 0, max(exp_vals) if exp_vals else 0) * 1.5
    if max_val == 0: max_val = 1
    
    # Symmetric ticks for butterfly chart
    tick_vals = [-max_val, -max_val/2, 0, max_val/2, max_val]
    def format_abs_tick(v):
        a = abs(v)
        if a >= 1e12: return f"{a/1e12:,.0f}T KHR"
        if a >= 1e9:  return f"{a/1e9:,.0f}B KHR"
        if a >= 1e6:  return f"{a/1e6:,.0f}M KHR"
        return f"{a:,.0f} KHR"
    tick_text = [format_abs_tick(v) for v in tick_vals]
    
    fig.update_layout(
        barmode='relative',
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": text_color, "family": "Arial"}},
        height=255,
        margin={"l": 20, "r": 20, "t": 40, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 11},
        xaxis={
            "showline": False, 
            "showgrid": True, 
            "gridcolor": grid_color, 
            "range": [-max_val, max_val], 
            "showticklabels": True, 
            "tickmode": "array",
            "tickvals": tick_vals,
            "ticktext": tick_text,
            "zeroline": True, 
            "zerolinecolor": "rgba(128,128,128,0.4)", "zerolinewidth": 2,
            "tickfont": {"color": label_color}
        },
        yaxis={"showline": False, "showgrid": False, "type": "category", "showticklabels": False},
        showlegend=True,
        legend={
            "orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1,
            "font": {"color": label_color}
        },
        transition={'duration': 1200, 'easing': 'cubic-in-out'}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_net_summary_chart(rev_summary, exp_summary, title):
    rev_val = rev_summary["Implementation"]
    exp_val = exp_summary["Implementation"]
    net_val = rev_val - exp_val
    
    categories = ['Revenue', 'Expense', 'Net']
    values = [rev_val, exp_val, net_val]
    # Green for Revenue, Red for Expense, Blue for positive Net, Orange for negative Net
    colors = ['#00AD4E', '#00A8E1', '#1f6bff' if net_val >= 0 else '#ff9300']
    
    is_dark = st.session_state.theme == 'dark'
    data_label_color = 'white' if is_dark else '#1e293b'

    fig = go.Figure(data=[
        go.Bar(
            x=categories, 
            y=values, 
            marker_color=colors,
            marker_line=dict(width=1, color='rgba(255,255,255,0.2)'),
            text=[f"{v:,.0f} KHR" for v in values],
            textposition='outside',
            cliponaxis=False,
            textfont=dict(color=data_label_color, size=11),
            hovertemplate='<b>%{x}</b><br>Amount: %{y:,.0f} KHR<extra></extra>'
        )
    ])
    
    max_val = max(abs(rev_val), abs(exp_val), abs(net_val))
    y_range = [min(0, net_val) * 1.2, max_val * 1.2] if max_val > 0 else [0, 1]
    
    is_dark = st.session_state.theme == 'dark'
    text_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b" # Light black
    grid_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": text_color, "family": "Arial"}},
        height=255, margin={"l": 20, "r": 20, "t": 40, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 12},
        xaxis={
            "showline": False, "showgrid": False,
            "tickfont": {"color": label_color}
        },
        yaxis={
            "showline": False, "showgrid": True, "gridcolor": grid_color, 
            "ticksuffix": " KHR", "tickformat": ".0s", "range": y_range,
            "tickfont": {"color": label_color}
        },
        showlegend=False,
        transition={'duration': 1200, 'easing': 'cubic-in-out'}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


# =========================
# Main Layout Composition
# =========================

is_dark = st.session_state.theme == 'dark'
theme_icon = "🌞" if is_dark else "🌙"
theme_label = "Light Mode" if is_dark else "Dark Mode"

# Header Rows - Using columns for precise horizontal layout
header_col1, header_col2 = st.columns([6, 4])

with header_col1:
    html(f'''
        <div style="padding-top: 0.2rem;">
            <div class='dashboard-title'>FMIS -  Expense & Revenue Dashboard</div>
            <div class='dashboard-subtitle'>Expense and Revenue Integrated Monitoring | Year 2025</div>
        </div>
    ''')

with header_col2:
    # Sub-grid for [Theme Toggle, Source, Live]
    # Spacing adjusted: Toggle (1.3), Source (1.2), Live (0.9)
    btn_col, src_col, live_col = st.columns([1.3, 1.2, 0.9])
    
    with btn_col:
        st.button(f"{theme_icon} {theme_label}", key="theme_toggle", on_click=toggle_theme, width='stretch')
    
    with src_col:
        html(f'''
            <div style="background: rgba(32, 214, 255, 0.1); border: 1px solid rgba(32, 214, 255, 0.3); padding: 0.5rem 0.6rem; border-radius: 6px; color: #20d6ff; font-size: 0.7rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; backdrop-filter: blur(4px); text-align: center; height: 38px; display: flex; align-items: center; justify-content: center;">
                Source: FMIS
            </div>
        ''')
        
    with live_col:
        html(f'''
            <div style="background: rgba(0, 173, 78, 0.1); border: 1px solid rgba(0, 173, 78, 0.3); padding: 0.5rem 0.6rem; border-radius: 6px; color: #00AD4E; font-size: 0.7rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 0.4rem; letter-spacing: 1px; text-transform: uppercase; backdrop-filter: blur(4px); height: 38px;">
                <span style="width: 7px; height: 7px; background: #00AD4E; border-radius: 50%; box-shadow: 0 0 8px #00AD4E; animation: livePulse 2s infinite ease-in-out;"></span>
                Live
            </div>
        ''')

# Spacer to separate header from content
st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)



# Top Section
top_left, top_right = st.columns([7, 3], gap="large")

with top_left:
    # KPI (summary) bar
    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "Financial Law - Expense", exp_summary["Financial Law"], "expense", "anim-delay-1")
    render_kpi(k2, "Modified Law - Expense", exp_summary["Modified Law"], "expense", "anim-delay-2")
    render_kpi(k3, "Financial Law - Revenue", rev_summary["Financial Law"], "revenue", "anim-delay-3")
    render_kpi(k4, "Modified Law - Revenue", rev_summary["Modified Law"], "revenue", "anim-delay-4")
    
    html("<div style='height: 0.5rem'></div>")
    
    # Financial ratio kpi: compare implementation and modified law, for expense and revenue separately
    r1, r2 = st.columns(2)
    render_ratio(r1, "Expense Execution Ratio", exp_summary["Implementation"], exp_summary["Modified Law"], "expense")
    render_ratio(r2, "Revenue Execution Ratio", rev_summary["Implementation"], rev_summary["Modified Law"], "revenue")

with top_right:
    # Process bar, right side of the kpi summary
    render_process_bar()



# Middle Section: Top 5 by category and organization side-by-side
c1, c2, c3, c4 = st.columns(4, gap="large")
with c1:
    render_top5_gauge_chart(exp_data["econ"], "Modified Law vs Implementation by Expense Types", is_expense=True)
with c2:
    render_top5_funnel_chart(exp_data["org"], "Implementation by Sectors (Expense)", is_expense=True, margin_left=100)
with c3:
    render_top5_gauge_chart(rev_data["econ"], "Top 5 implementation by Economic Class (Revenue)", is_expense=False)
with c4:
    render_top5_funnel_chart(rev_data["org"], "Top 5 implementation by Organizations (Revenue)", is_expense=False, margin_left=60)

# Bottom Section: Combined Trends & Additional Analysis
b1, b2, b3 = st.columns([10, 12, 8], gap="large")
with b1:
    render_combined_monthly_chart(exp_data["monthly"], rev_data["monthly"], "Monthly Trend (Rev vs Exp)")
with b2:
    render_quarterly_chart(exp_data["qtr"], rev_data["qtr"], "Quarterly Implementation (Rev vs Exp)")
with b3:
    render_net_summary_chart(rev_summary, exp_summary, "Revenue vs Expense vs Net")

html("<div class='footer-note' style='text-align:center; padding-top:0.5rem; padding-bottom:0.5rem;'>FMIS - Government Expense & Revenue Dashboard | Data Updated: 11-03-2026</div>")

# =========================
# Interval Loop (Kiosk Mode)
# =========================
# Triggers a full page reload every 35 seconds to "redo everything" (animations & data)
html('''
    <div id="refresh-indicator" style="
        position: fixed; 
        bottom: 0; left: 0; width: 0%; height: 2px; 
        background: var(--cyan); 
        z-index: 9999;
        transition: width 35s linear;
    "></div>
    <script>
        // Start the progress bar animation
        setTimeout(() => {
            document.getElementById('refresh-indicator').style.width = '100%';
        }, 100);

        // Reload the page after 35 seconds
        setTimeout(() => {
            window.location.reload();
        }, 35000);
    </script>
''')
