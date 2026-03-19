import streamlit as st

st.set_page_config(
    page_title="FMIS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Local imports
from styles import apply_custom_styles, html
from data import load_data, get_last_mod, get_overall, get_level
import components as comp


# =========================
# Apply Styling
# =========================
apply_custom_styles()

# =========================
# Data Loading & Processing
# =========================
exp_last_mod = get_last_mod("expense.xlsx")
rev_last_mod = get_last_mod("revenue.xlsx")

exp_data = load_data("expense.xlsx", exp_last_mod)
rev_data = load_data("revenue.xlsx", rev_last_mod)

exp_summary = get_overall(exp_data["gov"])
rev_summary = get_overall(rev_data["gov"])

exp_nat_impl, exp_nat_mod = get_level(exp_data["gov"], "National")
exp_sub_impl, exp_sub_mod = get_level(exp_data["gov"], "Sub-national")
rev_nat_impl, rev_nat_mod = get_level(rev_data["gov"], "National")
rev_sub_impl, rev_sub_mod = get_level(rev_data["gov"], "Sub-national")

# =========================
# Main Layout Composition
# =========================

is_dark = st.session_state.theme == 'dark'
theme_icon = "🌞" if is_dark else "🌙"
theme_label = "Light Mode" if is_dark else "Dark Mode"

# Header Rows
header_col1, header_col2 = st.columns([6, 4])

with header_col1:
    html(f'''
        <div style="padding-top: 0.2rem;">
            <div class='dashboard-title'>FMIS -  Expense & Revenue Dashboard</div>
            <div class='dashboard-subtitle'>Expense and Revenue Integrated Monitoring | Year 2026</div>
        </div>
    ''')

with header_col2:
    btn_col, src_col, live_col = st.columns([1.3, 1.2, 0.9])
    
    with btn_col:
        st.button(f"{theme_icon} {theme_label}", key="theme_toggle", on_click=toggle_theme, width='stretch')
    
    with src_col:
        html(f'''
            <div style="background: rgba(32, 214, 255, 0.1); border: 1px solid rgba(32, 214, 255, 0.3); padding: 0.5rem 0.6rem; border-radius: 6px; color: #20d6ff; font-size: 0.7rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; text-align: center; height: 38px; display: flex; align-items: center; justify-content: center;">
                Source: FMIS
            </div>
        ''')
        
    with live_col:
        html(f'''
            <div style="background: rgba(0, 173, 78, 0.1); border: 1px solid rgba(0, 173, 78, 0.3); padding: 0.5rem 0.6rem; border-radius: 6px; color: #00AD4E; font-size: 0.7rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 0.4rem; letter-spacing: 1px; text-transform: uppercase; height: 38px;">
                <span style="width: 7px; height: 7px; background: #00AD4E; border-radius: 50%; box-shadow: 0 0 8px #00AD4E; animation: livePulse 2s infinite ease-in-out;"></span>
                Live
            </div>
        ''')

st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)

# Top Section
top_left, top_right = st.columns([7, 3], gap="large")

with top_left:
    k1, k2, k3, k4 = st.columns(4)
    comp.render_kpi(k1, "Financial Law - Expense", exp_summary["Financial Law"], "expense", "anim-delay-1")
    comp.render_kpi(k2, "Modified Law - Expense", exp_summary["Modified Law"], "expense", "anim-delay-2")
    comp.render_kpi(k3, "Financial Law - Revenue", rev_summary["Financial Law"], "revenue", "anim-delay-3")
    comp.render_kpi(k4, "Modified Law - Revenue", rev_summary["Modified Law"], "revenue", "anim-delay-4")
    
    html("<div style='height: 0.5rem'></div>")
    
    r1, r2 = st.columns(2)
    comp.render_ratio(r1, "Expense Execution Ratio", exp_summary["Implementation"], exp_summary["Modified Law"], "expense")
    comp.render_ratio(r2, "Revenue Execution Ratio", rev_summary["Implementation"], rev_summary["Modified Law"], "revenue")

with top_right:
    comp.render_process_bar(
        exp_nat_impl, exp_nat_mod, exp_sub_impl, exp_sub_mod,
        rev_nat_impl, rev_nat_mod, rev_sub_impl, rev_sub_mod
    )

# Middle Section
c1, c2, c3, c4 = st.columns(4, gap="small")
with c1:
    comp.render_top5_gauge_chart(exp_data["econ"], "Modified Law vs Implementation by Expense Types", is_expense=True)
with c2:
    comp.render_top5_funnel_chart(exp_data["org"], "Implementation by Sectors (Expense)", is_expense=True, margin_left=95)
with c3:
    comp.render_top5_gauge_chart(rev_data["econ"], "Implementation by Revenue Types", is_expense=False)
with c4:
    comp.render_top5_funnel_chart(rev_data["org"], "Top 5 implementation by Organizations (Revenue)", is_expense=False, margin_left=55)

# Bottom Section
# Bottom Section - 2026 & 2025
c1, c2, c3, c4 = st.columns(4, gap="small")
with c1:
    comp.render_combined_monthly_chart(exp_data["monthly_2026"], rev_data["monthly_2026"], "Monthly Trend (Rev vs Exp) - 2026")
with c2:
    comp.render_combined_monthly_chart(exp_data["monthly_2025"], rev_data["monthly_2025"], "Monthly Trend (Rev vs Exp) - 2025")
with c3:
    comp.render_quarterly_chart(exp_data["qtr_2026"], rev_data["qtr_2026"], "Quarterly Trend (Rev vs Exp) - 2026")
with c4:
    comp.render_quarterly_chart(exp_data["qtr_2025"], rev_data["qtr_2025"], "Quarterly Trend (Rev vs Exp) - 2025")

html("<div class='footer-note' style='text-align:center; padding-top:0.5rem; padding-bottom:0.5rem;'>FMIS - Government Expense & Revenue Dashboard | Data Updated: 19-03-2026</div>")

# =========================
# Interval Loop (Kiosk Mode)
# =========================
html('''
    <div id="refresh-indicator" style="
        position: fixed; 
        bottom: 0; left: 0; width: 0%; height: 2px; 
        background: var(--cyan); 
        z-index: 9999;
        transition: width 30s linear;
    "></div>
    <script>
        setTimeout(() => {
            document.getElementById('refresh-indicator').style.width = '100%';
        }, 100);

        setTimeout(() => {
            window.location.reload();
        }, 30000);
    </script>
''')
