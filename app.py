import streamlit as st
import plotly.graph_objects as go
from textwrap import dedent
import pandas as pd
import os

st.set_page_config(
    page_title="FMIS Dashboard",
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
    if value >= 1_000_000_000_000:
        return f"៛{value / 1_000_000_000_000:,.1f}T"
    if value >= 1_000_000_000:
        return f"៛{value / 1_000_000_000:,.1f}B"
    if value >= 1_000_000:
        return f"៛{value / 1_000_000:,.1f}M"
    if value >= 1_000:
        return f"៛{value / 1_000:,.1f}K"
    return f"៛{value:,.0f}"


def format_summary(value: float) -> str:
    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:,.2f}T"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:,.0f}M"
    return f"{value:,.0f}"


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
            font-size: 1.6rem;
            font-weight: 800;
            color: #f5f7ff;
            line-height: 1.1;
            margin: 0 0 0.1rem 0;
            padding-left: 0.2rem;
            animation: fadeInDown 0.8s ease-out;
        }

        .dashboard-subtitle {
            text-align: left;
            font-size: 0.8rem;
            color: var(--cyan);
            margin-bottom: 0.2rem;
            padding-left: 0.2rem;
            animation: fadeInDown 1s ease-out;
        }

        /* KPI Cards */
        .kpi-card {
            background: linear-gradient(135deg, rgba(58, 77, 108, 0.95), rgba(26, 45, 74, 0.95));
            border-radius: 12px;
            padding: 0.8rem 1rem;
            text-align: center;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out backwards;
        }

        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(32, 214, 255, 0.15);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 4px;
            background: linear-gradient(90deg, #20d6ff, #1f6bff);
        }
        
        .kpi-card.expense::before {
            background: linear-gradient(90deg, #ff5a5a, #ff9300);
        }
        .kpi-card.revenue::before {
            background: linear-gradient(90deg, #11ba7a, #20d6a2);
        }

        .kpi-label {
            font-size: 0.95rem;
            font-weight: 700;
            color: #67ebff;
            margin-bottom: 0.6rem;
            letter-spacing: 0.5px;
        }
        .kpi-card.expense .kpi-label { color: #ff9b9b; }
        .kpi-card.revenue .kpi-label { color: #8affc2; }

        .kpi-value {
            font-size: 2.2rem;
            font-weight: 900;
            line-height: 1;
            color: #ffffff;
            margin-bottom: 0.2rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .anim-delay-1 { animation-delay: 0.1s; }
        .anim-delay-2 { animation-delay: 0.2s; }
        .anim-delay-3 { animation-delay: 0.3s; }
        .anim-delay-4 { animation-delay: 0.4s; }

        /* Progress Process bar */
        .process-container {
            background: rgba(26, 45, 74, 0.6);
            border-radius: 12px;
            padding: 0.8rem 1rem;
            border: 1px solid rgba(92, 132, 184, 0.35);
            animation: fadeInUp 0.8s ease-out backwards;
            animation-delay: 0.5s;
        }
        
        .process-title {
            color: #ff9b9b;
            font-size: 1.1rem;
            font-weight: 800;
            margin-bottom: 1.2rem;
            text-align: center;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .process-row {
            margin-bottom: 1.2rem;
        }

        .process-label-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            font-weight: 600;
            color: #edf6ff;
            margin-bottom: 0.4rem;
        }

        .process-track {
            width: 100%;
            height: 12px;
            border-radius: 999px;
            background: rgba(0, 0, 0, 0.4);
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
        }

        .process-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #ff5656, #ff9300);
            box-shadow: 0 0 10px rgba(255, 86, 86, 0.5);
            position: relative;
            animation: fillBar 1.5s ease-out forwards;
            transform-origin: left;
        }
        
        .process-fill::after {
            content: '';
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shine 2s infinite linear;
        }

        @keyframes fillBar {
            from { transform: scaleX(0); }
            to { transform: scaleX(1); }
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* Top 1 Chart Animations */
        .element-container:has(.top-bar-anim) + .element-container g.points > g:last-child path,
        .element-container:has(.top-bar-anim) + .element-container g.points > path:last-child {
            animation: topPulseOpacity 1.2s infinite alternate ease-in-out !important;
        }

        .element-container:has(.top-pie-anim) + .element-container g.slice:first-of-type path {
            animation: topPulseOpacity 1.2s infinite alternate ease-in-out !important;
        }

        @keyframes topPulseOpacity {
            0% { opacity: 1; }
            100% { opacity: 0.4; }
        }
        
        /* Plotly charts styling */
        div[data-testid="stPlotlyChart"] { 
            margin-top: 0.5rem;
            border-radius: 12px;
            border: 1px solid rgba(92, 132, 184, 0.2);
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));
            transition: border-color 0.3s ease;
        }
        div[data-testid="stPlotlyChart"]:hover {
            border-color: rgba(32, 214, 255, 0.5);
        }

        /* Ratio Cards */
        .ratio-card {
            background: rgba(26, 45, 74, 0.8);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 0.5rem;
            border: 1px solid rgba(92, 132, 184, 0.3);
            display: flex;
            align-items: center;
            justify-content: space-around;
            animation: fadeInUp 0.8s ease-out backwards;
            animation-delay: 0.4s;
        }
        .ratio-info { text-align: left; }
        .ratio-title { font-size: 0.9rem; color: #a0c4ff; font-weight: 600; text-transform: uppercase;}
        .ratio-value { font-size: 2.2rem; font-weight: 900; color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.3);}
        .ratio-subtitle { font-size: 0.75rem; color: #789bc7; }
        
        .ratio-circle {
            position: relative;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: conic-gradient(var(--fill-color) calc(var(--pct) * 1%), rgba(255,255,255,0.1) 0);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5), 0 0 15px var(--glow-color);
        }
        .ratio-circle::before {
            content: '';
            position: absolute;
            width: 65px;
            height: 65px;
            background: #1a2d4a;
            border-radius: 50%;
        }
        .ratio-circle-text {
            position: relative;
            font-size: 1.1rem;
            font-weight: 800;
            color: white;
            z-index: 10;
        }

        /* Global pulse for markers */
        .js-line path.point {
            animation: markerPulse 2s infinite ease-in-out;
        }
        @keyframes markerPulse {
            0% { transform: scale(1); filter: brightness(1); }
            50% { transform: scale(1.2); filter: brightness(1.5); }
            100% { transform: scale(1); filter: brightness(1); }
        }
        
        @keyframes livePulse {
            0% { opacity: 0.4; box-shadow: 0 0 0px var(--green); }
            50% { opacity: 1; box-shadow: 0 0 10px var(--green); }
            100% { opacity: 0.4; box-shadow: 0 0 0px var(--green); }
        }
    </style>
    '''
)

# =========================
# Data Loading & Processing
# =========================
@st.cache_data(ttl=300) # Cache expires every 5 mins to detect Excel changes automatically
def load_data(file_name):
    file_path = os.path.join("data_set", file_name)
    xls = pd.ExcelFile(file_path)
    
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

    return {
        "gov": get_clean_sheet("Sheet 1"),
        "monthly": get_clean_sheet("Sheet 2"),
        "org": get_clean_sheet("Sheet 3"),
        "econ": get_clean_sheet("Sheet 4"),
        "qtr": get_clean_sheet("Sheet 5"),
    }

exp_data = load_data("expense.xlsx")
rev_data = load_data("revenue.xlsx")

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
            <div class='kpi-card {type_class} {delay_class}'>
                <div class='kpi-label'>{title}</div>
                <div class='kpi-value'>{format_summary(value)}</div>
            </div>
            '''
        )

def render_ratio(col, title, impl, mod, type_class):
    ratio = (impl / mod) * 100 if mod > 0 else 0
    ratio = min(ratio, 100)
    
    color = "#ff5656" if type_class == 'expense' else "#20d6a2"
    
    with col:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = ratio,
            number = {'suffix': "%", 'font': {'size': 32, 'color': 'white', 'family': 'Arial Black'}},
            title = {'text': title, 'font': {'size': 14, 'color': '#a0c4ff'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
                'bar': {'color': color},
                'bgcolor': "rgba(0,0,0,0.2)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.1)",
                'steps': [
                    {'range': [0, 100], 'color': 'rgba(255,255,255,0.05)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 3},
                    'thickness': 0.75,
                    'value': ratio
                }
            }
        ))
        
        fig.update_layout(
            height=180,
            margin=dict(l=30, r=30, t=50, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "white", 'family': "Arial"}
        )
        
        # Wrapping Plotly gauge in the ratio-card container for style consistency
        st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
        html(f"<div style='text-align:center; color:#789bc7; font-size:0.8rem; margin-top:-1.5rem; padding-bottom:0.5rem;'>Implementation / Modified Law</div>")

def render_process_row(label, value, target, is_expense=True):
    pct = (value / target * 100) if target > 0 else 0
    display_pct = min(pct, 100)
    color = "linear-gradient(90deg, #ff5656, #ff9300)" if is_expense else "linear-gradient(90deg, #11ba7a, #20d6ff)"
    glow = "rgba(255, 86, 86, 0.5)" if is_expense else "rgba(17, 186, 122, 0.5)"
    label_color = "#ff9b9b" if is_expense else "#8affc2"
    
    return "".join([
        "<div class='process-row' style='margin-bottom: 0.8rem;'>",
        "<div class='process-label-row'>",
        f"<span>{label} <span style='font-size: 0.75rem; opacity: 0.7; color: #fff;'>({pct:.1f}%)</span></span>",
        f"<span style='color:{label_color}'>{format_money(value)}</span>",
        "</div>",
        "<div class='process-track'>",
        f"<div class='process-fill' style='width:{display_pct}%; background:{color}; box-shadow: 0 0 10px {glow};'></div>",
        "</div>",
        "</div>"
    ])

def render_process_bar():
    exp_body = ""
    exp_body += render_process_row("National Level", exp_nat_impl, exp_nat_mod, is_expense=True)
    exp_body += render_process_row("Sub-National Level", exp_sub_impl, exp_sub_mod, is_expense=True)
    
    rev_body = ""
    rev_body += render_process_row("National Level", rev_nat_impl, rev_nat_mod, is_expense=False)
    rev_body += render_process_row("Sub-National Level", rev_sub_impl, rev_sub_mod, is_expense=False)
    
    html(
        f'''
        <div class="process-container">
            <div class="process-title" style="color: #ff9b9b; margin-bottom: 0.8rem;">Expense Implementation</div>
            {exp_body}
            <div style="height: 1rem;"></div>
            <div class="process-title" style="color: #8affc2; margin-bottom: 0.8rem;">Revenue Implementation</div>
            {rev_body}
        </div>
        '''
    )


def render_top5_chart(df, title, is_expense=True):
    df_sorted = df.sort_values(by="IMPLEMENTATION", ascending=True).tail(5)
    categories = df_sorted["ACCOUNT"].astype(str).tolist()
    values = df_sorted["IMPLEMENTATION"].tolist()
    
    # Use gradients for bars to make them "fancy"
    base_color = '#ff5656' if is_expense else '#20d6a2'
    glow_color = 'rgba(255, 86, 86, 0.3)' if is_expense else 'rgba(32, 214, 162, 0.3)'
    
    max_val = max(values) if values else 1
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=categories, x=values, orientation='h',
        marker=dict(
            color=base_color,
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=[format_money(v) for v in values],
        textposition='outside',
        textfont=dict(color='white', size=11, weight='bold'),
        hovertemplate='<b>%{y}</b><br>Amount: ៛%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={"text": title, "font": {"size": 13, "color": "#ffffff", "family": "sans-serif"}},
        height=230,
        margin={"l": 20, "r": 100, "t": 40, "b": 10}, # Increased right margin to 100
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dcecff", "size": 11},
        xaxis={
            "showline": False, 
            "showgrid": True, 
            "gridcolor": "rgba(255,255,255,0.05)", 
            "tickprefix": "៛", 
            "tickformat": ",.0s",
            "range": [0, max_val * 1.3] # Add 30% padding to the right for labels
        },
        yaxis={"showline": False, "showgrid": False, "type": "category"},
        showlegend=False,
        # Fancy transition
        transition={'duration': 1000, 'easing': 'cubic-in-out'}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_top5_pie_chart(df, title, is_expense=True):
    df_sorted = df.sort_values(by="IMPLEMENTATION", ascending=False).head(5)
    labels = df_sorted["BUSINESS_UNIT"].astype(str).tolist()
    labels = [l[:15] + '..' if len(l) > 15 else l for l in labels]
    values = df_sorted["IMPLEMENTATION"].tolist()
    
    if is_expense:
        # Use a more sophisticated "Rose/Crimson" palette instead of yellow-red
        colors = ['#ff4d4d', '#ff7b7b', '#ff9b9b', '#ffbbbb', '#ffdbdb']
        direction = 'clockwise'
    else:
        colors = ['#11ba7a', '#20d6a2', '#48cae4', '#08c6df', '#1f6bff']
        direction = 'counterclockwise'
        
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6, # Create high-end Donut look
        pull=[0.05, 0, 0, 0, 0],
        direction=direction,
        textinfo='percent',
        textposition='inside',
        marker=dict(colors=colors, line=dict(color='rgba(255,255,255,0.1)', width=2)),
        hovertemplate='<b>%{label}</b><br>Amount: ៛%{value:,.0f}<extra></extra>'
    )])
    
    fig.update_layout(
        title={"text": title, "font": {"size": 13, "color": "#ffffff", "family": "sans-serif"}},
        height=240, # Slightly increased height for better legend spacing
        margin={"l": 10, "r": 10, "t": 45, "b": 50}, # Increased bottom margin for legend room
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dcecff", "size": 10},
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.25, # Pushed legend further down
            xanchor="center", 
            x=0.5,
            font=dict(size=9)
        ),
        # Fancy transition
        transition={'duration': 1000, 'easing': 'cubic-in-out'},
        annotations=[dict(text='TOP 5', x=0.5, y=0.5, font_size=16, showarrow=False, font_color='white', font_family='Arial Black')]
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_combined_monthly_chart(df_exp, df_rev, title):
    df_merged = pd.merge(df_exp, df_rev, on="MONTH_NAME", suffixes=("_EXP", "_REV"), how="outer")
    months = df_merged["MONTH_NAME"].astype(str).tolist()
    exp_values = df_merged["IMPLEMENTATION_EXP"].fillna(0).tolist()
    rev_values = df_merged["IMPLEMENTATION_REV"].fillna(0).tolist()
    
    fig = go.Figure()
    
    # Base traces
    fig.add_trace(go.Scatter(
        x=months, y=rev_values, name='Revenue', mode='lines+markers',
        line={"color": '#20d6a2', "width": 3, "shape": "spline", "smoothing": 1}, 
        marker={"size": 10, "color": "#ffffff", "line": {"width": 2, "color": '#20d6a2'}},
        fill='tozeroy', fillcolor='rgba(32, 214, 162, 0.10)',
        hovertemplate='<b>%{x}</b><br>Revenue: ៛%{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=months, y=exp_values, name='Expense', mode='lines+markers',
        line={"color": '#ff5656', "width": 3, "shape": "spline", "smoothing": 1}, 
        marker={"size": 10, "color": "#ffffff", "line": {"width": 2, "color": '#ff5656'}},
        fill='tozeroy', fillcolor='rgba(255, 86, 86, 0.10)',
        hovertemplate='<b>%{x}</b><br>Expense: ៛%{y:,.0f}<extra></extra>'
    ))

    # Add Movement: Animate drawing the line
    fig.update_layout(
        title={"text": title, "font": {"size": 13, "color": "#ffffff", "family": "sans-serif"}},
        height=320,
        margin={"l": 20, "r": 20, "t": 35, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dcecff", "size": 11},
        xaxis={"showline": False, "showgrid": False, "type": "category"},
        yaxis={"showline": False, "showgrid": True, "gridcolor": "rgba(255,255,255,0.05)", "tickprefix": "៛", "tickformat": ",.0s"},
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )

    # Transition settings for fancy reveal
    fig.update_layout(transition={'duration': 1000, 'easing': 'cubic-in-out'})
    
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_quarterly_chart(df_exp, df_rev, title):
    df_merged = pd.merge(df_exp, df_rev, on="QUARTER_NAME", suffixes=("_EXP", "_REV"), how="outer")
    qtrs = df_merged["QUARTER_NAME"].astype(str).tolist()
    exp_vals = df_merged["IMPLEMENTATION_EXP"].fillna(0).tolist()
    rev_vals = df_merged["IMPLEMENTATION_REV"].fillna(0).tolist()
    
    neg_exp_vals = [-v for v in exp_vals]
    rev_text = [f"៛{v/1000000000:,.1f}B" if v>=1000000000 else f"៛{v/1000000:,.0f}M" for v in rev_vals]
    exp_text = [f"៛{v/1000000000:,.1f}B" if v>=1000000000 else f"៛{v/1000000:,.0f}M" for v in exp_vals]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=qtrs, x=neg_exp_vals, orientation='h', name='Expense',
        marker=dict(color='#ff5656', line=dict(color='rgba(255,255,255,0.1)', width=1)),
        text=exp_text, textposition='outside', textfont=dict(color='#ff9b9b'),
        hovertemplate='<b>%{y}</b><br>Expense: ៛%{customdata:,.0f}<extra></extra>',
        customdata=exp_vals
    ))
    fig.add_trace(go.Bar(
        y=qtrs, x=rev_vals, orientation='h', name='Revenue',
        marker=dict(color='#20d6a2', line=dict(color='rgba(255,255,255,0.1)', width=1)),
        text=rev_text, textposition='outside', textfont=dict(color='#8affc2'),
        hovertemplate='<b>%{y}</b><br>Revenue: ៛%{x:,.0f}<extra></extra>'
    ))
    
    max_val = max(max(rev_vals) if rev_vals else 0, max(exp_vals) if exp_vals else 0) * 1.3
    if max_val == 0: max_val = 1
    
    fig.update_layout(
        barmode='relative',
        title={"text": title, "font": {"size": 13, "color": "#ffffff", "family": "sans-serif"}},
        height=320,
        margin={"l": 40, "r": 20, "t": 45, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dcecff", "size": 11},
        xaxis={"showline": False, "showgrid": True, "gridcolor": "rgba(255,255,255,0.05)", "range": [-max_val, max_val], "showticklabels": False, "zeroline": True, "zerolinecolor": "rgba(255,255,255,0.2)"},
        yaxis={"showline": False, "showgrid": False, "type": "category", "tickfont": dict(weight='bold')},
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def render_net_summary_chart(rev_summary, exp_summary, title):
    rev_val = rev_summary["Implementation"]
    exp_val = exp_summary["Implementation"]
    net_val = rev_val - exp_val
    
    categories = ['Revenue', 'Expense', 'Net']
    values = [rev_val, exp_val, net_val]
    # Green for Revenue, Red for Expense, Blue for positive Net, Orange for negative Net
    colors = ['#20d6a2', '#ff5656', '#1f6bff' if net_val >= 0 else '#ff9300']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories, 
            y=values, 
            marker_color=colors,
            marker_line=dict(width=1, color='rgba(255,255,255,0.2)'),
            text=[f"៛{v/1000000000:,.1f}B" if abs(v)>=1000000000 else f"៛{v/1000000:,.0f}M" for v in values],
            textposition='outside',
            textfont=dict(color='white', size=11, weight='bold'),
            hovertemplate='<b>%{x}</b><br>Amount: ៛%{y:,.0f}<extra></extra>'
        )
    ])
    
    max_val = max(abs(rev_val), abs(exp_val), abs(net_val))
    y_range = [min(0, net_val) * 1.2, max_val * 1.2] if max_val > 0 else [0, 1]
    
    fig.update_layout(
        title={"text": title, "font": {"size": 13, "color": "#ffffff", "family": "sans-serif"}},
        height=320, margin={"l": 20, "r": 20, "t": 40, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dcecff", "size": 12},
        xaxis={"showline": False, "showgrid": False},
        yaxis={"showline": False, "showgrid": True, "gridcolor": "rgba(255,255,255,0.05)", "tickprefix": "៛", "tickformat": ",.0s", "range": y_range},
        showlegend=False
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


# =========================
# Main Layout Composition
# =========================

html(
    f'''
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; padding: 0.2rem 0.5rem 0 0.5rem;">
        <div>
            <div class='dashboard-title'>FMIS -  Expense & Revenue Dashboard</div>
            <div class='dashboard-subtitle'>Expense and Revenue Integrated Monitoring | Year 2025</div>
        </div>
        <div style="display: flex; gap: 0.8rem; align-items: center; padding-top: 0.3rem;">
            <div style="background: rgba(32, 214, 255, 0.1); border: 1px solid rgba(32, 214, 255, 0.3); padding: 0.4rem 1rem; border-radius: 6px; color: #20d6ff; font-size: 0.7rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; backdrop-filter: blur(4px);">Source: FMIS</div>
            <div style="background: rgba(17, 186, 122, 0.1); border: 1px solid rgba(17, 186, 122, 0.3); padding: 0.4rem 1rem; border-radius: 6px; color: #11ba7a; font-size: 0.7rem; font-weight: 800; display: flex; align-items: center; gap: 0.5rem; letter-spacing: 1px; text-transform: uppercase; backdrop-filter: blur(4px);">
                <span style="width: 8px; height: 8px; background: #11ba7a; border-radius: 50%; box-shadow: 0 0 8px #11ba7a; animation: livePulse 2s infinite ease-in-out;"></span>
                Live
            </div>
        </div>
    </div>
    '''
)

# Top Section
top_left, top_right = st.columns([7, 3], gap="large")

with top_left:
    # KPI (summary) bar
    k1, k2, k3, k4 = st.columns(4)
    render_kpi(k1, "Financial Law - Expense", exp_summary["Financial Law"], "expense", "anim-delay-1")
    render_kpi(k2, "Financial Law - Revenue", rev_summary["Financial Law"], "revenue", "anim-delay-2")
    render_kpi(k3, "Modified Law - Expense", exp_summary["Modified Law"], "expense", "anim-delay-3")
    render_kpi(k4, "Modified Law - Revenue", rev_summary["Modified Law"], "revenue", "anim-delay-4")
    
    html("<div style='height: 0.5rem'></div>")
    
    # Financial ratio kpi: compare implementation and modified law, for expense and revenue separately
    r1, r2 = st.columns(2)
    render_ratio(r1, "Expense Execution Ratio", exp_summary["Implementation"], exp_summary["Modified Law"], "expense")
    render_ratio(r2, "Revenue Execution Ratio", rev_summary["Implementation"], rev_summary["Modified Law"], "revenue")

with top_right:
    # Process bar, right side of the kpi summary
    render_process_bar()

html("<div style='height: 0.8rem'></div>")

# Middle Section: Top 5 by category and organization side-by-side
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    render_top5_chart(exp_data["econ"], "Top 5 implementation by Economic Class (Expense)", is_expense=True)
with c2:
    render_top5_chart(rev_data["econ"], "Top 5 implementation by Economic Class (Revenue)", is_expense=False)
with c3:
    render_top5_pie_chart(exp_data["org"], "Top 5 implementation by Organizations (Expense)", is_expense=True)
with c4:
    render_top5_pie_chart(rev_data["org"], "Top 5 implementation by Organizations (Revenue)", is_expense=False)

html("<div style='height: 0.5rem'></div>")

# Bottom Section: Combined Trends & Additional Analysis
b1, b2, b3 = st.columns(3, gap="large")
with b1:
    render_combined_monthly_chart(exp_data["monthly"], rev_data["monthly"], "Monthly Trend (Rev vs Exp)")
with b2:
    render_quarterly_chart(exp_data["qtr"], rev_data["qtr"], "Quarterly Implementation (Rev vs Exp)")
with b3:
    render_net_summary_chart(rev_summary, exp_summary, "Revenue vs Expense vs Net")

html("<div class='footer-note' style='text-align:center; padding-top:0.5rem; padding-bottom:0.5rem;'>FMIS - Government Expense & Revenue Dashboard | Data Updated: 11-03-2026</div>")
