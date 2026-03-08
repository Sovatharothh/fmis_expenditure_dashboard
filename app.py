import streamlit as st
import plotly.graph_objects as go
from textwrap import dedent

st.set_page_config(
    page_title="Government Budget Expense Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# Helpers
# =========================
def html(block: str):
    st.markdown(dedent(block).strip(), unsafe_allow_html=True)


def format_money(value: float) -> str:
    if value >= 1_000_000:
        return f"៛{value / 1_000_000:,.0f}M"
    if value >= 1_000:
        return f"៛{value / 1_000:,.0f}K"
    return f"៛{value:,.0f}"


def format_summary(value: float) -> str:
    if value >= 1_000_000:
        return f"{round(value / 1_000_000):,.0f}M"
    if value >= 1_000:
        return f"{round(value / 1_000):,.0f}K"
    return f"{round(value):,.0f}"


# =========================
# Styling
# =========================
html(
    '''
    <style>
        :root {
            --bg: #04122b;
            --panel: #1a2d4a;
            --card: #374d6c;
            --text: #e9f2ff;
            --cyan: #20d6ff;
            --blue: #1f6bff;
            --teal: #08c6df;
            --green: #11ba7a;
            --orange: #ff9300;
            --red: #ff5a5a;
            --border: rgba(92, 132, 184, 0.35);
        }

        /* Hide Streamlit default header / toolbar */
        header[data-testid="stHeader"] { display: none !important; height: 0 !important; }
        [data-testid="stToolbar"] { display: none !important; }
        .stAppToolbar { display: none !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }

        .stApp {
            background: linear-gradient(180deg, #020c1c 0%, #061731 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1920px;
            padding-top: 0.1rem !important;
            padding-bottom: 0.1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 0.6rem;
        }

        div[data-testid="column"] {
            padding: 0 !important;
        }

        /* Header */
        .dashboard-title {
            text-align: left;
            font-size: 1.8rem;
            font-weight: 800;
            color: #f5f7ff;
            line-height: 1.1;
            margin: 0 0 0.1rem 0;
            padding-left: 0.2rem;
        }

        .dashboard-subtitle {
            text-align: left;
            font-size: 0.8rem;
            color: var(--cyan);
            margin-bottom: 0.4rem;
            padding-left: 0.2rem;
        }

        /* Summary */
        .summary-header {
            background: rgba(31,78,160,0.5);
            border: 1px solid rgba(36, 220, 255, 0.2);
            border-radius: 8px;
            padding: 0.4rem 0.6rem;
            margin-bottom: 0.3rem;
        }

        .summary-header-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: #59e9ff;
            margin: 0;
        }

        .summary-card {
            background: rgba(58, 77, 108, 0.95);
            border-radius: 8px;
            padding: 0.8rem 0.3rem;
            text-align: center;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border: 1px solid rgba(255,255,255,0.03);
        }

        .summary-card.priority {
            background: #ff8b00;
            border: 1px solid rgba(255,255,255,0.24);
        }

        .summary-label {
            font-size: 0.9rem;
            font-weight: 700;
            color: #67ebff;
            margin-bottom: 0.4rem;
        }

        .summary-value {
            font-size: 2.0rem;
            font-weight: 800;
            line-height: 1;
            color: #21e1ff;
            margin-bottom: 0.3rem;
        }

        .summary-foot {
            font-size: 0.7rem;
            color: #d4e6fb;
        }

        .summary-card.priority .summary-label,
        .summary-card.priority .summary-value,
        .summary-card.priority .summary-foot {
            color: #ffffff;
        }

        /* Section headers */
        .class-header {
            border-radius: 8px;
            padding: 0.4rem 0.6rem;
            margin: 0.4rem 0 0.4rem 0;
            color: white;
            background: linear-gradient(90deg, rgba(40,72,184,0.7) 0%, rgba(12,160,198,0.7) 50%, rgba(8,164,111,0.7) 100%);
        }

        .class-title {
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0;
        }

        .class-sub {
            font-size: 0.65rem;
            opacity: 0.95;
        }

        /* Panel shell */
        .panel-marker { display: none; }

        .panel-title {
            color: var(--cyan);
            font-size: 0.95rem;
            font-weight: 800;
            margin: 0 0 0.4rem 0;
        }

        .year-card {
            background: #374d6c;
            border-radius: 8px;
            padding: 0.8rem;
            min-height: 250px;
        }

        .year-title {
            text-align: center;
            color: #56e7ff;
            font-size: 0.95rem;
            font-weight: 800;
            margin-bottom: 0.8rem;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            gap: 0.4rem;
            font-size: 0.8rem;
            font-weight: 600;
            color: #edf6ff;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            color: #42edff;
            font-weight: 800;
            white-space: nowrap;
        }

        .progress-track {
            width: 100%;
            height: 8px;
            border-radius: 999px;
            background: rgba(144, 170, 210, 0.23);
            overflow: hidden;
            margin-bottom: 0.85rem;
        }

        .progress-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #16c3ff, #2e8fff);
        }

        .footer-note {
            text-align: right;
            color: #acc5e3;
            font-size: 0.70rem;
            margin-top: -0.5rem;
            margin-right: 0.5rem;
        }

        /* Style only the real panel containers */
        div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div:has(.panel-marker) {
            background: #1a2d4a;
            border-radius: 8px;
            border: 1px solid rgba(92, 132, 184, 0.35);
            padding: 0.6rem;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
        }

        div[data-testid="stPlotlyChart"] { 
            margin-top: -0.1rem;
            border-radius: 8px;
            border: 1px solid rgba(92, 132, 184, 0.35);
            overflow: hidden;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
        }
    </style>
    '''
)

# =========================
# Data Loading & Processing
# =========================
import pandas as pd
import os

@st.cache_data
def load_data():
    file_path = os.path.join("data_set", "data.xlsx")
    xls = pd.ExcelFile(file_path)
    
    # helper to clean df
    def get_clean_sheet(sheet_name_hint):
        sheet = [s for s in xls.sheet_names if sheet_name_hint in s][0]
        df = pd.read_excel(xls, sheet_name=sheet)
        df.columns = df.columns.str.strip()
        if '' in df.columns:
            df = df.drop(columns=[''])
        for col in df.columns:
            if col not in ['GOV_LEVEL', 'MONTH_NAME', 'BUSINESS_UNIT', 'ACCOUNT', 'QUARTER_NAME']:
                if df[col].dtype == 'object':
                    s = df[col].astype(str).str.strip()
                    s = s.str.replace(r'[\'"]', '', regex=True)
                    s = s.str.replace(',', '', regex=True)
                    s = s.str.replace(r'^\((.*)\)$', r'-\1', regex=True)
                    s = s.replace('-', '0')
                    df[col] = pd.to_numeric(s, errors='coerce').fillna(0)
        return df

    df_gov = get_clean_sheet("Sheet 1")
    df_monthly = get_clean_sheet("Sheet 2")
    df_org = get_clean_sheet("Sheet 3")
    df_econ = get_clean_sheet("Sheet 4")
    df_qtr = get_clean_sheet("Sheet 5")
    
    return df_gov, df_monthly, df_org, df_econ, df_qtr

df_gov, df_monthly, df_org, df_econ, df_qtr = load_data()

metrics_order = [
    "Financial Law",
    "Adjustment",
    "Transfer",
    "Modified Law",
    "Implementation",
    "Available Budget",
]

def build_overall_summary():
    row = df_gov[df_gov['GOV_LEVEL'].str.strip() == 'All'].iloc[0]
    return {
        "Financial Law": row["ORIGINAL_BUDGET"],
        "Adjustment": row["ADJUSTMENT_BUDGET"],
        "Transfer": row["TRANSFER_BUDGET"],
        "Modified Law": row["CURRENT_BUDGET"],
        "Implementation": row["IMPLEMENTATION"],
        "Available Budget": row["AVAILABLE_BUDGET"],
    }

def build_total_class():
    combined = {}
    for lvl, name in [('National', 'National Level'), ('Sub-national', 'Sub-National Level'), ('APE', 'APE Level')]:
        rows = df_gov[df_gov['GOV_LEVEL'].str.strip() == lvl]
        if not rows.empty:
            row = rows.iloc[0]
            val = {
                "Financial Law": row["ORIGINAL_BUDGET"],
                "Adjustment": row["ADJUSTMENT_BUDGET"],
                "Transfer": row["TRANSFER_BUDGET"],
                "Modified Law": row["CURRENT_BUDGET"],
                "Implementation": row["IMPLEMENTATION"],
                "Available Budget": row["AVAILABLE_BUDGET"],
            }
        else:
            val = {m: 0 for m in metrics_order}
            
        combined[name] = {"2025": val}
    return combined


# =========================
# Render functions
# =========================
def render_progress_metric(label, value, max_value):
    pct = 0 if max_value == 0 else min(value / max_value * 100, 100)
    return dedent(
        f'''
        <div class='metric-row'>
            <span>{label}</span>
            <span class='metric-value'>{format_money(value)}</span>
        </div>
        <div class='progress-track'>
            <div class='progress-fill' style='width:{pct}%;'></div>
        </div>
        '''
    ).strip()


def render_year_card(year, values, max_value):
    body = "".join(render_progress_metric(m, values[m], max_value) for m in metrics_order)
    html(
        f'''
        <div class='year-card'>
            <div class='year-title'>Year {year}</div>
            {body}
        </div>
        '''
    )


def render_level_panel(level_name, class_level_data, key_prefix):
    y26 = class_level_data["2025"]
    max_value = max(list(y26.values()))

    with st.container():
        html("<div class='panel-marker'></div>")
        html(f"<div class='panel-title'>{level_name}</div>")
        render_year_card("2025", y26, max_value)


def render_summary(summary):
    html(
        '''
        <div class='summary-header'>
            <div class='summary-header-title'>Overall Summary</div>
        </div>
        '''
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    cards = [
        (c1, "Financial Law", format_summary(summary["Financial Law"]), False),
        (c2, "Adjustment", format_summary(summary["Adjustment"]), False),
        (c3, "Transfer", format_summary(summary["Transfer"]), False),
        (c4, "Modified Law", format_summary(summary["Modified Law"]), False),
        (c5, "Implementation", format_summary(summary["Implementation"]), True),
        (c6, "Available Budget", format_summary(summary["Available Budget"]), False),
    ]

    for col, label, value, priority in cards:
        with col:
            cls = "summary-card priority" if priority else "summary-card"
            html(
                f'''
                <div class='{cls}'>
                    <div class='summary-label'>{label}</div>
                    <div class='summary-value'>{value}</div>
                    <div class='summary-foot'>Total Allocation</div>
                </div>
                '''
            )


# =========================
# Additional Graphs (Compacted for 1080p Grid Layout)
# =========================

def render_budget_utilization():
    # Sheet 4: Top Economic Class
    df_econ_sorted = df_econ.sort_values(by="IMPLEMENTATION", ascending=True).tail(10)
    categories = df_econ_sorted["ACCOUNT"].astype(str).tolist()
    values = df_econ_sorted["IMPLEMENTATION"].tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=categories, x=values, orientation='h',
        marker=dict(color='#20d6a2'),
        text=[f"៛{v/1000000:,.0f}M" for v in values],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Amount: ៛%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={"text": "Top 10 most spent by Economic class", "font": {"size": 12, "color": "#3beaff"}},
        height=220,
        margin={"l": 60, "r": 40, "t": 30, "b": 20},
        paper_bgcolor="#1a2d4a", plot_bgcolor="#1a2d4a",
        font={"color": "#dcecff", "size": 10},
        xaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "gridcolor": "rgba(255,255,255,0.05)", "tickprefix": "៛", "tickformat": ",.0s"},
        yaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "type": "category"},
        showlegend=False
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_monthly_trend():
    months = df_monthly["MONTH_NAME"].astype(str).tolist()
    expenses = df_monthly["IMPLEMENTATION"].tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=expenses, mode='lines+markers',
        line={"color": "#20d6ff", "width": 2}, marker={"size": 6, "color": "#20d6ff"},
        fill='tozeroy', fillcolor='rgba(32, 214, 255, 0.1)',
        hovertemplate='<b>%{x}</b><br>Expense: ៛%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title={"text": "Monthly Expense Trend 2025", "font": {"size": 12, "color": "#3beaff"}},
        height=220,
        margin={"l": 40, "r": 20, "t": 30, "b": 20},
        paper_bgcolor="#1a2d4a", plot_bgcolor="#1a2d4a",
        font={"color": "#dcecff", "size": 10},
        xaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "gridcolor": "rgba(255,255,255,0.05)", "type": "category"},
        yaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "gridcolor": "rgba(255,255,255,0.05)", "tickprefix": "៛", "tickformat": ",.0s"},
        showlegend=False
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_top_departments():
    df_org_sorted = df_org.sort_values(by="IMPLEMENTATION", ascending=True).tail(5)
    departments = df_org_sorted["BUSINESS_UNIT"].astype(str).tolist()
    budgets = df_org_sorted["IMPLEMENTATION"].tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=departments, x=budgets, orientation='h',
        marker={"color": ['#1f6bff', '#08c6df', '#20d6ff', '#16c3ff', '#2e8fff']},
        text=[f"៛{b/1000000:,.0f}M" for b in budgets], textposition='inside',
        hovertemplate='<b>%{y}</b><br>Budget: ៛%{x:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title={"text": "Top 5 Most Spent by organizations", "font": {"size": 12, "color": "#3beaff"}},
        height=220,
        margin={"l": 65, "r": 20, "t": 30, "b": 20},
        paper_bgcolor="#1a2d4a", plot_bgcolor="#1a2d4a",
        font={"color": "#dcecff", "size": 10},
        xaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "gridcolor": "rgba(255,255,255,0.05)", "tickprefix": "៛", "tickformat": ",.0s"},
        yaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "type": "category"},
        showlegend=False
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_budget_vs_implementation():
    categories = df_qtr["QUARTER_NAME"].astype(str).tolist()
    implementation = df_qtr["IMPLEMENTATION"].tolist()
    
    fig = go.Figure()
    colors = ['#ffae14', '#20d6a2', '#22b8ff', '#ff5656']
    fig.add_trace(go.Bar(
        x=categories, y=implementation, name='Implemented', 
        marker={"color": colors},
        text=[f"៛{v/1000000:,.0f}M" for v in implementation],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Amount: ៛%{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title={"text": "Implementation by Qtr", "font": {"size": 12, "color": "#3beaff"}},
        barmode='group', height=240,
        margin={"l": 40, "r": 20, "t": 30, "b": 40},
        paper_bgcolor="#1a2d4a", plot_bgcolor="#1a2d4a",
        font={"color": "#dcecff", "size": 10},
        xaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "gridcolor": "rgba(255,255,255,0.05)", "type": "category"},
        yaxis={"showline": True, "linecolor": "rgba(215,230,255,0.2)", "gridcolor": "rgba(255,255,255,0.05)", "tickprefix": "៛", "tickformat": ",.0s"},
        legend={"orientation": "h", "yanchor": "top", "y": -0.15, "xanchor": "center", "x": 0.5, "font": {"size": 9}}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_budget_distribution(summary):
    budget_movement = summary["Adjustment"] + summary["Transfer"]
    categories = ['Financial Law', 'Budget Movement', 'Modified Law', 'Implementation', 'Available Budget']
    values = [summary['Financial Law'], budget_movement, summary['Modified Law'], summary['Implementation'], summary['Available Budget']]
    colors = ['#22b8ff', '#24d2ff', '#20d6a2', '#ffae14', '#ff5656']
    fig = go.Figure(data=[go.Pie(
        labels=categories, values=values, marker={"colors": colors},
        textposition='inside', textinfo='percent', hole=0.4,
        hovertemplate='<b>%{label}</b><br>Amount: ៛%{value:,.0f}<extra></extra>'
    )])
    fig.update_layout(
        title={"text": "Budget Distribution 2025", "font": {"size": 12, "color": "#3beaff"}},
        height=260,
        margin={"l": 10, "r": 10, "t": 30, "b": 10},
        paper_bgcolor="#1a2d4a", plot_bgcolor="#1a2d4a",
        font={"color": "#dcecff", "size": 10},
        showlegend=True,
        legend={"orientation": "h", "yanchor": "top", "y": -0.05, "xanchor": "center", "x": 0.5, "font": {"size": 9}}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

# =========================
# Main Layout Composition
# =========================

html("<div class='dashboard-title'>Cambodia FMIS - Budget Execution Dashboard</div>")
html("<div class='dashboard-subtitle'>National, Sub-National, and APE Level Analysis | Year 2025</div>")

summary = build_overall_summary()
combined_total_class = build_total_class()

# Grid Layout: Left Column (70%) and Right Column (30%)
left_col, right_col = st.columns([7, 3], gap="medium")

with left_col:
    # 1. Top Summary metrics (spans the entire left column)
    render_summary(summary)
    
    st.write("") # small spacing
    
    # 2. Level Panels

    c1, c2, c3 = st.columns(3)
    with c1: render_level_panel("National Level", combined_total_class["National Level"], "TOTAL-NAT")
    with c2: render_level_panel("Sub-National Level", combined_total_class["Sub-National Level"], "TOTAL-SUB")
    with c3: render_level_panel("APE Level", combined_total_class["APE Level"], "TOTAL-APE")

    st.write("") # small spacing

    # 3. Two Bottom Graphs for Left Column
    g1, g2 = st.columns(2)
    with g1:
        render_budget_utilization()
    with g2:
        render_monthly_trend()

with right_col:
    # Right column gets the other 3 graphs stacked vertically. We use the same card CSS.
    render_budget_distribution(summary)
    render_top_departments()
    render_budget_vs_implementation()

html("<div class='footer-note'>FMIS - Government Expense Dashboard | Data Updated: 3/7/2025</div>")
