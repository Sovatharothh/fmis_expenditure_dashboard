import streamlit as st
from textwrap import dedent

def html(block: str):
    st.markdown(dedent(block).strip(), unsafe_allow_html=True)

def apply_custom_styles():
    is_light = st.session_state.theme == 'light'

    # Define theme colors based on state
    theme_vars = {
        "bg": "#F0F2F6" if is_light else "#04122b",
        "panel": "#FFFFFF" if is_light else "#1a2d4a",
        "card": "#FFFFFF" if is_light else "#374d6c",
        "text": "#1e293b" if is_light else "#e9f2ff",
        "cyan": "#3498dc" if is_light else "#20d6ff",
        "blue": "#3498dc" if is_light else "#00A8E1",
        "green": "#1abc9c" if is_light else "#00AD4E",
        "border": "#e2e8f0" if is_light else "rgba(92, 132, 184, 0.6)",
        "kpi_bg": "#FFFFFF" if is_light else "linear-gradient(135deg, rgba(58, 77, 108, 0.95), rgba(26, 45, 74, 0.95))",
        "shadow": "none",
        "app_bg": "#F0F2F6" if is_light else "linear-gradient(180deg, #020c1c 0%, #061731 100%)",
        "chart_bg": "#FFFFFF" if is_light else "linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4))",
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
                border: 1px solid var(--border);
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
                padding: 1.2rem;
                border: 1px solid var(--border);
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
                margin-bottom: 0.2rem;
                border-radius: 12px;
                border: 1px solid var(--border);
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
                0%   {{ opacity: 0.4; filter: brightness(1) drop-shadow(0 0 0px var(--cyan)); }}
                50%  {{ opacity: 1.0; filter: brightness(1.6) drop-shadow(0 0 12px var(--cyan)); }}
                100% {{ opacity: 0.4; filter: brightness(1) drop-shadow(0 0 0px var(--cyan)); }}
            }}
        </style>
        '''
    )
