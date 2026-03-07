import streamlit as st
import plotly.graph_objects as go
from copy import deepcopy
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
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.2f}K"
    return f"${value:,.0f}"


def format_summary(value: float) -> str:
    if value >= 1_000_000:
        return f"{round(value / 1_000_000):.0f}M"
    if value >= 1_000:
        return f"{round(value / 1_000):.0f}K"
    return f"{round(value):.0f}"


# =========================
# Styling
# =========================
html(
    """
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
        header[data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }

        .stAppToolbar {
            display: none !important;
        }

        #MainMenu {
            visibility: hidden !important;
        }

        footer {
            visibility: hidden !important;
        }

        .stApp {
            background: linear-gradient(180deg, #020c1c 0%, #061731 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1920px;
            padding-top: 0.4rem !important;
            padding-bottom: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 0.75rem;
        }

        div[data-testid="column"] {
            padding: 0 !important;
        }

        /* Header */
        .dashboard-title {
            text-align: center;
            font-size: 2.75rem;
            font-weight: 800;
            color: #f5f7ff;
            line-height: 1.08;
            margin: 0 0 0.15rem 0;
        }

        .dashboard-subtitle {
            text-align: center;
            font-size: 0.95rem;
            color: var(--cyan);
            margin-bottom: 0.7rem;
        }

        .legend-wrap {
            display: flex;
            justify-content: center;
            gap: 2.2rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }

        .legend-box {
            text-align: center;
            min-width: 105px;
            color: #acc5e3;
            font-size: 0.72rem;
        }

        .legend-swatch {
            width: 38px;
            height: 24px;
            border-radius: 4px;
            display: inline-block;
            margin: 0.22rem 0;
        }

        /* Summary */
        .summary-header {
            background: linear-gradient(90deg, #1f4ea0 0%, #125a75 100%);
            border: 1px solid rgba(36, 220, 255, 0.4);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.4rem;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
        }

        .summary-header-title {
            font-size: 1.7rem;
            font-weight: 800;
            color: #59e9ff;
            margin: 0;
        }

        .summary-card {
            background: rgba(58, 77, 108, 0.95);
            border-radius: 10px;
            padding: 0.95rem 0.55rem;
            text-align: center;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border: 1px solid rgba(255,255,255,0.03);
        }

        .summary-card.priority {
            background: #ff8b00;
            border: 2px solid rgba(255,255,255,0.24);
        }

        .summary-label {
            font-size: 0.78rem;
            font-weight: 700;
            color: #67ebff;
            margin-bottom: 0.28rem;
        }

        .summary-note {
            font-size: 0.65rem;
            color: #ffffff;
            margin-bottom: 0.14rem;
        }

        .summary-value {
            font-size: 1.95rem;
            font-weight: 800;
            line-height: 1;
            color: #21e1ff;
            margin-bottom: 0.22rem;
        }

        .summary-foot {
            font-size: 0.66rem;
            color: #d4e6fb;
        }

        .summary-card.priority .summary-label,
        .summary-card.priority .summary-value,
        .summary-card.priority .summary-foot {
            color: #ffffff;
        }

        /* Section headers */
        .class-header {
            border-radius: 10px;
            padding: 0.95rem 1rem;
            margin: 0.9rem 0 0.7rem 0;
            color: white;
        }

        .class-a { background: #2545b7; }
        .class-b { background: #0b9cc5; }
        .class-c { background: #05a36f; }
        .class-total { background: linear-gradient(90deg, #2848b8 0%, #0ca0c6 50%, #08a46f 100%); }

        .class-title {
            font-size: 1.35rem;
            font-weight: 800;
            margin-bottom: 0.08rem;
        }

        .class-sub {
            font-size: 0.75rem;
            opacity: 0.95;
        }

        /* Panel shell */
        .panel-marker {
            display: none;
        }

        .panel-title {
            color: var(--cyan);
            font-size: 1.12rem;
            font-weight: 800;
            margin: 0 0 0.75rem 0;
        }

        .year-card {
            background: #374d6c;
            border-radius: 10px;
            padding: 0.72rem;
            min-height: 230px;
        }

        .year-title {
            text-align: center;
            color: #56e7ff;
            font-size: 0.92rem;
            font-weight: 800;
            margin-bottom: 0.65rem;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            gap: 0.5rem;
            font-size: 0.72rem;
            font-weight: 600;
            color: #edf6ff;
            margin-bottom: 0.22rem;
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
            margin-bottom: 0.72rem;
        }

        .progress-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #16c3ff, #2e8fff);
        }

        .mini-divider {
            border-top: 1px solid rgba(166, 193, 227, 0.28);
            margin: 0.8rem 0 0.65rem;
        }

        .chart-title {
            color: #3beaff;
            font-size: 0.9rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .footer-note {
            text-align: center;
            color: #acc5e3;
            font-size: 0.76rem;
            margin-top: 0.9rem;
        }

        /* Style only the real panel containers */
        div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div:has(.panel-marker) {
            background: #1a2d4a;
            border-radius: 14px;
            border: 1px solid rgba(92, 132, 184, 0.35);
            padding: 0.8rem;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
            min-height: 640px;
        }

        /* Plot spacing */
        div[data-testid="stPlotlyChart"] {
            margin-top: -0.05rem;
        }

        @media (max-width: 1300px) {
            div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div:has(.panel-marker) {
                min-height: auto;
            }
        }
    </style>
    """
)

# =========================
# Data
# =========================
base_class_data = {
    "Class A": {
        "color_class": "class-a",
        "share": "6%",
        "2025": {
            "Financial Law": 3000000,
            "Budget Movement": 450000,
            "Modified Law": 600000,
            "Implementation": 2400000,
            "Available Budget": 750000,
        },
        "2026": {
            "Financial Law": 3300000,
            "Budget Movement": 472500,
            "Modified Law": 648000,
            "Implementation": 2690000,
            "Available Budget": 817500,
        },
    },
    "Class B": {
        "color_class": "class-b",
        "share": "7%",
        "2025": {
            "Financial Law": 3500000,
            "Budget Movement": 625000,
            "Modified Law": 700000,
            "Implementation": 2800000,
            "Available Budget": 875000,
        },
        "2026": {
            "Financial Law": 3850000,
            "Budget Movement": 651250,
            "Modified Law": 756000,
            "Implementation": 3140000,
            "Available Budget": 953750,
        },
    },
    "Class C": {
        "color_class": "class-c",
        "share": "2%",
        "2025": {
            "Financial Law": 1000000,
            "Budget Movement": 150000,
            "Modified Law": 200000,
            "Implementation": 800000,
            "Available Budget": 250000,
        },
        "2026": {
            "Financial Law": 1100000,
            "Budget Movement": 157500,
            "Modified Law": 216000,
            "Implementation": 896000,
            "Available Budget": 272500,
        },
    },
}

levels = ["National Level", "Sub-National Level", "APE Level"]
metrics_order = [
    "Financial Law",
    "Budget Movement",
    "Modified Law",
    "Implementation",
    "Available Budget",
]
metric_colors = {
    "Financial Law": "#22b8ff",
    "Budget Movement": "#24d2ff",
    "Modified Law": "#20d6a2",
    "Implementation": "#ffae14",
    "Available Budget": "#ff5656",
}


def duplicate_across_levels(class_data):
    return {level: deepcopy(class_data) for level in levels}


all_data = {klass: duplicate_across_levels(data) for klass, data in base_class_data.items()}


def build_total_class(all_classes):
    total = {
        "color_class": "class-total",
        "share": "15%",
        "2025": {m: 0 for m in metrics_order},
        "2026": {m: 0 for m in metrics_order},
    }

    for _, level_map in all_classes.items():
        national = level_map["National Level"]
        for year in ["2025", "2026"]:
            for metric in metrics_order:
                total[year][metric] += national[year][metric]

    return duplicate_across_levels(total)


def build_overall_summary(all_classes):
    summary = {m: 0 for m in metrics_order}
    for _, level_map in all_classes.items():
        national = level_map["National Level"]
        for year in ["2025", "2026"]:
            for metric in metrics_order:
                summary[metric] += national[year][metric]
    return summary


# =========================
# Render functions
# =========================
def render_progress_metric(label, value, max_value):
    pct = 0 if max_value == 0 else min(value / max_value * 100, 100)
    return dedent(
        f"""
        <div class='metric-row'>
            <span>{label}</span>
            <span class='metric-value'>{format_money(value)}</span>
        </div>
        <div class='progress-track'>
            <div class='progress-fill' style='width:{pct}%;'></div>
        </div>
        """
    ).strip()


def render_year_card(year, values, max_value):
    body = "".join(render_progress_metric(m, values[m], max_value) for m in metrics_order)
    html(
        f"""
        <div class='year-card'>
            <div class='year-title'>Year {year}</div>
            {body}
        </div>
        """
    )


def render_budget_chart(year_2025, year_2026, key):
    fig = go.Figure()
    x = ["2025", "2026"]

    for metric in metrics_order:
        fig.add_bar(
            x=x,
            y=[year_2025[metric], year_2026[metric]],
            name=metric,
            marker_color=metric_colors[metric],
        )

    fig.update_layout(
        barmode="group",
        height=210,
        margin=dict(l=6, r=6, t=6, b=6),
        paper_bgcolor="#1a2d4a",
        plot_bgcolor="#1a2d4a",
        font=dict(color="#dcecff", size=11),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.28,
            xanchor="center",
            x=0.5,
            font=dict(size=9),
        ),
        xaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
            tickfont=dict(size=9),
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key,
        config={"displayModeBar": False},
    )


def render_level_panel(level_name, class_level_data, key_prefix):
    y26 = class_level_data["2026"]
    max_value = max(list(y26.values()))

    with st.container():
        html("<div class='panel-marker'></div>")
        html(f"<div class='panel-title'>{level_name}</div>")

        render_year_card("2026", y26, max_value)


def render_summary(summary):
    html(
        """
        <div class='summary-header'>
            <div class='summary-header-title'>Overall Summary </div>
        </div>
        """
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    cards = [
        (c1, "Financial Law", format_summary(summary["Financial Law"]), False),
        (c2, "Budget Movement", format_summary(summary["Budget Movement"]), False),
        (c3, "Modified Law", format_summary(summary["Modified Law"]), False),
        (c4, "Implementation", format_summary(summary["Implementation"]), True),
        (c5, "Available Budget", format_summary(summary["Available Budget"]), False),
    ]

    for col, label, value, priority in cards:
        with col:
            if priority:
                html(
                    f"""
                    <div class='summary-card priority'>
                        <div class='summary-label'>{label}</div>
                        <div class='summary-value'>{value}</div>
                        <div class='summary-foot'>Total Allocation</div>
                    </div>
                    """
                )
            else:
                html(
                    f"""
                    <div class='summary-card'>
                        <div class='summary-label'>{label}</div>
                        <div class='summary-value'>{value}</div>
                        <div class='summary-foot'>Total Allocation</div>
                    </div>
                    """
                )


def render_class_section(title, subtitle_class, class_data, key_prefix, color_class):
    html(
        f"""
        <div class='class-header {color_class}'>
            <div class='class-title'>{title}</div>
            <div class='class-sub'>{subtitle_class}</div>
        </div>
        """
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_level_panel("National Level", class_data["National Level"], f"{key_prefix}-NAT")
    with c2:
        render_level_panel("Sub-National Level", class_data["Sub-National Level"], f"{key_prefix}-SUB")
    with c3:
        render_level_panel("APE Level", class_data["APE Level"], f"{key_prefix}-APE")


# =========================
# Header
# =========================
html("<div class='dashboard-title'>Government Budget Expense Dashboard</div>")
html("<div class='dashboard-subtitle'>National, Sub-National, and APE Level Analysis | Years 2025-2026</div>")

# =========================
# Summary
# =========================
summary = build_overall_summary(all_data)
render_summary(summary)

# =========================
# Total section
# =========================
combined_total_class = build_total_class(all_data)
render_class_section(
    "Total of All Classes (A + B + C)",
    "Budget Classification and Allocation",
    combined_total_class,
    "TOTAL",
    "class-total",
)



# =========================
# Additional Graphs
# =========================

# Graph 1: Budget Utilization Rate by Category
def render_budget_utilization():
    fig = go.Figure()
    
    categories = ["Implementation", "Modified Law", "Available Budget"]
    values = [2690000, 648000, 817500]
    total = sum(values)
    utilization_pct = [(v/total)*100 for v in values]
    
    fig.add_trace(go.Bar(
        y=categories,
        x=values,
        orientation='h',
        marker=dict(color=['#ffae14', '#20d6a2', '#ff5656']),
        text=[f"${v/1000000:.2f}M ({p:.1f}%)" for v, p in zip(values, utilization_pct)],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Amount: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Budget Utilization by Category",
        height=350,
        margin=dict(l=150, r=100, t=50, b=50),
        paper_bgcolor="#1a2d4a",
        plot_bgcolor="#1a2d4a",
        font=dict(color="#dcecff", size=11),
        xaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)",
            tickformat="$,.0f"
        ),
        yaxis=dict(showline=True, linecolor="rgba(215,230,255,0.45)"),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Graph 2: Monthly Expense Trend
def render_monthly_trend():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    expenses = [1800000, 2100000, 1900000, 2300000, 2500000, 2200000, 2450000, 2100000, 1900000, 2400000, 2600000, 2800000]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=expenses,
        mode='lines+markers',
        name='Monthly Expense',
        line=dict(color='#20d6ff', width=3),
        marker=dict(size=8, color='#20d6ff'),
        fill='tozeroy',
        fillcolor='rgba(32, 214, 255, 0.1)',
        hovertemplate='<b>%{x}</b><br>Expense: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Monthly Expense Trend 2026",
        height=350,
        margin=dict(l=60, r=40, t=50, b=50),
        paper_bgcolor="#1a2d4a",
        plot_bgcolor="#1a2d4a",
        font=dict(color="#dcecff", size=11),
        xaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)"
        ),
        yaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)",
            tickformat="$,.0f"
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Graph 3: Top Departments by Budget
def render_top_departments():
    departments = ['Ministry A', 'Ministry B', 'Ministry C', 'Ministry D', 'Ministry E']
    budgets = [2690000, 2450000, 2100000, 1800000, 1500000]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=departments,
        x=budgets,
        orientation='h',
        marker=dict(color=['#1f6bff', '#08c6df', '#20d6ff', '#16c3ff', '#2e8fff']),
        text=[format_money(b) for b in budgets],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Budget: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Top 5 Departments by Budget Allocation",
        height=350,
        margin=dict(l=150, r=100, t=50, b=50),
        paper_bgcolor="#1a2d4a",
        plot_bgcolor="#1a2d4a",
        font=dict(color="#dcecff", size=11),
        xaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)",
            tickformat="$,.0f"
        ),
        yaxis=dict(showline=True, linecolor="rgba(215,230,255,0.45)"),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Graph 4: Budget vs Implementation Comparison
def render_budget_vs_implementation():
    categories = ['Q1', 'Q2', 'Q3', 'Q4']
    budget_allocated = [2500000, 2700000, 2600000, 2800000]
    implementation = [2400000, 2500000, 2300000, 2600000]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=budget_allocated,
        name='Budget Allocated',
        marker_color='#1f6bff',
        hovertemplate='<b>%{x}</b><br>Budget: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=implementation,
        name='Implementation',
        marker_color='#ffae14',
        hovertemplate='<b>%{x}</b><br>Implementation: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Budget Allocated vs Implementation by Quarter",
        barmode='group',
        height=350,
        margin=dict(l=60, r=40, t=50, b=50),
        paper_bgcolor="#1a2d4a",
        plot_bgcolor="#1a2d4a",
        font=dict(color="#dcecff", size=11),
        xaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)"
        ),
        yaxis=dict(
            showline=True,
            linecolor="rgba(215,230,255,0.45)",
            gridcolor="rgba(255,255,255,0.10)",
            tickformat="$,.0f"
        ),
        legend=dict(orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Graph 5: Available Budget Distribution Pie Chart
def render_budget_distribution():
    categories = ['Financial Law', 'Budget Movement', 'Modified Law', 'Implementation', 'Available Budget']
    values = [3300000, 472500, 648000, 2690000, 817500]
    colors = ['#22b8ff', '#24d2ff', '#20d6a2', '#ffae14', '#ff5656']
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        marker=dict(colors=colors),
        textposition='auto',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Budget Distribution by Category 2026",
        height=400,
        margin=dict(l=60, r=60, t=80, b=60),
        paper_bgcolor="#1a2d4a",
        plot_bgcolor="#1a2d4a",
        font=dict(color="#dcecff", size=11),
        showlegend=True,
        legend=dict(orientation='v', yanchor='middle', y=0.5, xanchor='left', x=1.02)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# Display the 5 new graphs
st.write("")  # Spacing
col1, col2 = st.columns(2)
with col1:
    render_budget_utilization()
with col2:
    render_monthly_trend()

st.write("")  # Spacing
col3, col4 = st.columns(2)
with col3:
    render_top_departments()
with col4:
    render_budget_vs_implementation()

st.write("")  # Spacing
col5, _ = st.columns([1, 1])
with col5:
    render_budget_distribution()

html("<div class='footer-note'>FMIS - Government Expense Dashboard | Years 2025-2026 | Data Updated: 3/7/2026</div>")