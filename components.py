import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import json
import pandas as pd
from textwrap import dedent

from utils import format_money, format_summary, format_exact

def html(block: str):
    st.markdown(dedent(block).strip(), unsafe_allow_html=True)

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
                    "font": {"size": 13, "color": "#789bc7", "family": "Arial"}
                }
            ]
        )
        
        fig.data[0].value = 0 # Start at 0
        fig.data[0].gauge.threshold.value = 0 # Start at 0
        fig_json = fig.to_json()
        
        import random
        import string
        uid = ''.join(random.choices(string.ascii_lowercase, k=4))
        chart_uid = f"plotly_gauge_{uid}"
        
        bg_style = "background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));" if is_dark else "background: #FFFFFF;"
        border_color = "rgba(92, 132, 184, 0.6)" if is_dark else "#e2e8f0"
        
        html_str = f"""
        <style>
            body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; font-family: Arial, sans-serif; }}
            .plotly-anim-container {{
                border-radius: 12px;
                border: 1px solid {border_color};
                {bg_style}
                transition: border-color 0.3s ease;
                box-sizing: border-box;
                height: 235px;
                width: 100%;
                margin-top: 0.5rem;
            }}
            .plotly-anim-container:hover {{
                border-color: {"#20d6ff" if is_dark else "#3498dc"};
            }}
        </style>
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <div id="{chart_uid}" class="plotly-anim-container"></div>
        <script>
            var fig = {fig_json};
            var chartDiv = document.getElementById('{chart_uid}');
            var finalValue = {ratio};
            
            Plotly.newPlot(chartDiv, fig.data, fig.layout, {{displayModeBar: false, responsive: true}}).then(function() {{
                function triggerSweep() {{
                    Plotly.animate(chartDiv, {{
                        data: [{{value: finalValue, 'gauge.threshold.value': finalValue}}]
                    }}, {{
                        transition: {{
                            duration: 2000,
                            easing: 'cubic-in-out'
                        }},
                        frame: {{
                            duration: 2000,
                            redraw: false
                        }}
                    }});
                }}
                
                // Initial sweep
                setTimeout(triggerSweep, 500);
                
                // Repeat every 30s
                setInterval(function() {{
                    Plotly.update(chartDiv, {{value: [0], 'gauge.threshold.value': [0]}});
                    setTimeout(triggerSweep, 100);
                }}, 30000);
            }});
        </script>
        """
        
        components.html(html_str, height=245)

def render_process_row(label, value, target, is_expense=True, custom_gradient=None):
    pct = (value / target * 100) if target > 0 else 0
    display_pct = min(pct, 100)
    
    if not custom_gradient:
        color = "linear-gradient(90deg, #00A8E1, #33B9E7)" if is_expense else "linear-gradient(90deg, #00AD4E, #14C85D)"
    else:
        color = custom_gradient
        
    is_dark = st.session_state.theme == 'dark'
    text_color = "#edf6ff" if is_dark else "#1e293b"
    label_color = ("#67ebff" if is_dark else "#0284c7") if is_expense else ("#8affc2" if is_dark else "#059669")
    secondary_text = "#789bc7" if is_dark else "#475569"
    glow = "rgba(0, 168, 225, 0.3)" if is_expense else "rgba(0, 173, 78, 0.3)"
    
    return "".join([
        "<div class='process-row' style='margin-bottom: 0.1rem;'>",
        f"<div style='font-size: 0.85rem; font-weight: 600; color: {text_color}; margin-bottom: 0px;'>{label}</div>",
        "<div class='process-track' style='height: 10px; margin-bottom: 1px;'>",
        f"<div class='process-fill' style='width:{display_pct}%; background:{color}; box-shadow: 0 0 5px {glow}; border-radius: 4px;'></div>",
        "</div>",
        "<div style='display: flex; justify-content: space-between; align-items: baseline;'>",
        "<div>",
        f"<span style='color:{label_color}; font-size: 0.95rem; font-weight: 800;'>{format_money(value)}</span> ",
        f"<span style='color:{label_color}; font-size: 0.75rem; font-weight: 500; opacity: 0.9;'>({pct:.1f}%)</span>",
        "</div>",
        "<div style='text-align: right;'>",
        f"<span style='font-size: 0.6rem; color: #5c84b8; text-transform: uppercase; letter-spacing: 0.8px; margin-right: 4px;'>Modified Law</span>",
        f"<span style='font-size: 0.8rem; color: {secondary_text}; font-weight: 700;'>{format_money(target)}</span>",
        "</div>",
        "</div>",
        "</div>"
    ])

def render_process_bar(exp_nat_impl, exp_nat_mod, exp_sub_impl, exp_sub_mod, rev_nat_impl, rev_nat_mod, rev_sub_impl, rev_sub_mod):
    exp_body = ""
    exp_body += render_process_row("National Level", exp_nat_impl, exp_nat_mod, is_expense=True, 
                                   custom_gradient="linear-gradient(90deg, #00A8E1, #33B9E7)")
    exp_body += render_process_row("Sub-National Level", exp_sub_impl, exp_sub_mod, is_expense=True,
                                   custom_gradient="linear-gradient(90deg, #1f6bff, #67ebff)")
    
    rev_body = ""
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
    # Mapping for requested custom order
    preferred_order = [
        "Staff Charges",
        "Operating Expenditures",
        "Financial Charges",
        "Investment Expenditure",
        "Transfer Expenditure",
        "Other Expenditure"
    ]
    
    label_col = "EXPENDITURE_CATEGORY" if "EXPENDITURE_CATEGORY" in df.columns else "ACCOUNT"
    df_sorted = df[df[label_col].isin(preferred_order)].copy()
    df_sorted['sort_idx'] = df_sorted[label_col].map({v: i for i, v in enumerate(preferred_order)})
    df_sorted = df_sorted.sort_values('sort_idx').head(6)
    
    if df_sorted.empty:
        df_sorted = df.sort_values(by="IMPLEMENTATION", ascending=False).head(5)

    if is_expense:
        color_palette = ['#00A8E1', '#1A7BB8', '#33B9E7', '#56C1E8', '#80D4F2', '#A2E9FF']
    else:
        color_palette = ['#00863D', '#00AD4E', '#14C85D', '#32D475', '#52E08E', '#72ECA7']
    
    chart_data = []
    for i, row in enumerate(df_sorted.itertuples()):
        impl = float(getattr(row, "IMPLEMENTATION", 0))
        target = float(getattr(row, "MODIFIED_LAW", getattr(row, "CURRENT_BUDGET", 1)))
        pct = (impl / target * 100) if target > 0 else 0
        import textwrap
        label_val = getattr(row, "EXPENDITURE_CATEGORY", getattr(row, "ACCOUNT", "Unknown"))
        label = textwrap.fill(str(label_val), width=22)
        
        chart_data.append({
            "category": label,
            "value": round(float(pct), 1),
            "impl": f"{impl:,.0f} KHR",
            "target": f"{target:,.0f} KHR",
            "full": 100,
            "columnSettings": { "fill": color_palette[i % len(color_palette)] }
        })

    chart_data.reverse()
    chart_json = json.dumps(chart_data)
    
    import random
    import string
    uid = ''.join(random.choices(string.ascii_lowercase, k=4))
    chart_uid = f"gauge_{uid}"

    is_dark = st.session_state.theme == 'dark'
    bg_style = "background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));" if is_dark else "background: #FFFFFF;"
    title_color = "#ffffff" if is_dark else "#1e293b"
    track_color = "0x1a2d4a" if is_dark else "0xcccccc"
    tooltip_bg = "0x04122b" if is_dark else "0xFFFFFF"
    tooltip_stroke = "0x5c84b8" if is_dark else "0x3498dc"
    text_color_hex = "0xffffff" if is_dark else "0x1e293b"
    label_color_hex = "0xffffff" if is_dark else "0x1e293b"
    border_color = "rgba(92, 132, 184, 0.6)" if is_dark else "#e2e8f0"

    amcharts_html = f"""
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; font-family: Arial, sans-serif; }}
        .am-chart-container {{
            height: 300px;
            box-sizing: border-box;
            border-radius: 12px;
            border: 1px solid {border_color};
            {bg_style}
            padding: 8px 12px 0px 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
    </style>
    <div id="container_{chart_uid}" class="am-chart-container glow-sweep-canvas">
        <div style="width: 100%; color: {title_color}; font-size: 14px; font-weight: 800; margin-bottom: 2px; text-align: left; padding-left: 5px; font-family: Arial, sans-serif;">
            {title}
        </div>
        <div id="{chart_uid}" style="width: 100%; height: 270px;"></div>
    </div>
    
    <script src="https://cdn.amcharts.com/lib/5/index.js"></script>
    <script src="https://cdn.amcharts.com/lib/5/xy.js"></script>
    <script src="https://cdn.amcharts.com/lib/5/radar.js"></script>
    <script src="https://cdn.amcharts.com/lib/5/themes/Animated.js"></script>
    <script>
    am5.ready(function() {{
        var root = am5.Root.new("{chart_uid}");
        root.setThemes([am5themes_Animated.new(root)]);

        var chart = root.container.children.push(am5radar.RadarChart.new(root, {{
          panX: false, panY: false, wheelX: "none", wheelY: "none",
          innerRadius: am5.percent(30),
          startAngle: -90,
          endAngle: 180,
          paddingTop: 0,
          paddingBottom: 0
        }}));

        var xRenderer = am5radar.AxisRendererCircular.new(root, {{
          strokeOpacity: 0.1,
          minGridDistance: 80
        }});
        xRenderer.labels.template.setAll({{ 
          radius: 15, fill: am5.color({label_color_hex}), fontSize: 10, fontFamily: "Arial, sans-serif", fontWeight: "500",
          letterSpacing: 2.0
        }});

        var xAxis = chart.xAxes.push(am5xy.ValueAxis.new(root, {{
          renderer: xRenderer, min: 0, max: 100, strictMinMax: true, numberFormat: "#'%'",
        }}));

        var yRenderer = am5radar.AxisRendererRadial.new(root, {{ minGridDistance: 1 }});
        yRenderer.labels.template.setAll({{
          centerX: am5.p100, fontWeight: "500", fontSize: 10, fill: am5.color({label_color_hex}), 
          paddingRight: 20, fontFamily: "Arial, sans-serif",
          multiLine: true, width: 130, textAlign: "right",
          letterSpacing: 2.0
        }});
        yRenderer.grid.template.setAll({{ forceHidden: true }});

        var yAxis = chart.yAxes.push(am5xy.CategoryAxis.new(root, {{
          categoryField: "category", renderer: yRenderer
        }}));
        yAxis.data.setAll({chart_json});

        var series1 = chart.series.push(am5radar.RadarColumnSeries.new(root, {{
          xAxis: xAxis, yAxis: yAxis, clustered: false, valueXField: "full", categoryYField: "category",
          fill: am5.color({track_color}), fillOpacity: 0.45
        }}));
        series1.columns.template.setAll({{ width: am5.percent(100), strokeOpacity: 0, cornerRadius: 20 }});
        series1.data.setAll({chart_json});

        var tooltip = am5.Tooltip.new(root, {{
          getFillFromSprite: false,
          labelText: "[bold]{{category}}[/]\\nImplementation: {{impl}}\\nModified Law: {{target}}\\nRatio: {{valueX}}%"
        }});
        
        tooltip.label.setAll({{ fill: am5.color({text_color_hex}), fontSize: 12 }});
        tooltip.get("background").setAll({{
          fill: am5.color({tooltip_bg}),
          fillOpacity: 0.95,
          stroke: am5.color({tooltip_stroke}),
          strokeWidth: 2,
          strokeOpacity: 0.3
        }});

        var series2 = chart.series.push(am5radar.RadarColumnSeries.new(root, {{
          xAxis: xAxis, yAxis: yAxis, clustered: false, valueXField: "value", categoryYField: "category",
          sequencedInterpolation: true
        }}));
        series2.columns.template.setAll({{
          width: am5.percent(100), strokeOpacity: 0, cornerRadius: 20, templateField: "columnSettings",
          tooltipText: "[bold]{{category}}[/]\\nImplementation: {{impl}}\\nModified Law: {{target}}\\nRatio: {{valueX}}%",
          tooltip: tooltip
        }});
        series2.data.setAll({chart_json});

        function redoAnimation() {{
            series1.appear(1500, 100);
            series2.appear(1500, 200);
            chart.appear(1500, 100);
        }}

        redoAnimation();
        setInterval(redoAnimation, 30000);
        if(root._logo) {{ root._logo.dispose(); }}
    }});
    </script>
    """
    components.html(amcharts_html, height=310)

def render_top5_funnel_chart(df, title, is_expense=True, margin_left=80):
    df_sorted = df.sort_values(by="IMPLEMENTATION", ascending=False).head(5)
    label_col = "SECTOR" if "SECTOR" in df.columns else "BUSINESS_UNIT"
    import textwrap
    labels = [textwrap.fill(str(l), width=18).replace('\n', '<br>') for l in df_sorted[label_col]]
    values = df_sorted["IMPLEMENTATION"].tolist()
    
    formatted_text = [f"{v:,.0f} KHR" for v in values]

    if is_expense:
        colors = ['#00A8E1', '#1A7BB8', '#33B9E7', '#66CBED', '#80D4F2']
        connector_color = "rgba(0, 168, 225, 0.35)"
    else:
        colors = ['#00863D', '#00AD4E', '#14C85D', '#32D475', '#52E08E']
        connector_color = "rgba(0, 173, 78, 0.35)"
        
    fig = go.Figure(go.Funnel(
        y=labels, x=values, text=formatted_text, textinfo="text", textposition="auto",
        textfont={"color": '#ffffff' if st.session_state.theme == 'dark' else '#1e293b', "size": 10, "family": "Arial"},
        marker={"color": colors, "line": {"width": 1, "color": "rgba(255,255,255,0.2)"}},
        connector={"fillcolor": connector_color, "line": {"color": "rgba(255, 255, 255, 0.15)", "width": 1}},
        hovertemplate='<b>%{y}</b><br>Amount: %{x:,.0f} KHR<extra></extra>'
    ))
    
    is_dark = st.session_state.theme == 'dark'
    title_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b" 

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": title_color, "family": "Arial"}, "x": 0.05, "y": 0.92},
        height=300, 
        margin={"l": margin_left + 15, "r": 30, "t": 60, "b": 15}, 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 10},
        showlegend=False,
        transition={'duration': 1200, 'easing': 'cubic-in-out'}
    )
    
    fig.update_xaxes(visible=False)
    fig.update_yaxes(type='category', showgrid=False, zeroline=False, tickfont={"size": 11, "color": label_color})
    
    fig_json = fig.to_json()
    
    import random
    import string
    uid = ''.join(random.choices(string.ascii_lowercase, k=4))
    chart_uid = f"plotly_funnel_{uid}"
    
    bg_style = "background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));" if is_dark else "background: #FFFFFF;"
    border_color = "rgba(92, 132, 184, 0.6)" if is_dark else "#e2e8f0"
    
    html_str = f"""
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; font-family: Arial, sans-serif; }}
        .plotly-anim-container {{
            border-radius: 12px;
            border: 1px solid {border_color};
            {bg_style}
            transition: border-color 0.3s ease;
            box-sizing: border-box;
            height: 300px;
            width: 100%;
        }}
        .plotly-anim-container:hover {{
            border-color: {"#20d6ff" if is_dark else "#3498dc"};
            box-shadow: 0 10px 20px rgba(32, 214, 255, 0.15);
        }}
        
        @keyframes shakeFunnel {{
            0%, 100% {{ transform: translateX(0); }}
            10%, 30%, 50%, 70%, 90% {{ transform: translateX(-6px); }}
            20%, 40%, 60%, 80% {{ transform: translateX(6px); }}
        }}
        
        .shake-active .trace.funnel .points path, .shake-active g.points path {{
            animation: shakeFunnel 2s cubic-bezier(.36,.07,.19,.97) both;
            transform-origin: center center;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div id="{chart_uid}" class="plotly-anim-container glow-sweep-canvas"></div>
    <script>
        var fig = {fig_json};
        var chartDiv = document.getElementById('{chart_uid}');
        
        Plotly.newPlot(chartDiv, fig.data, fig.layout, {{displayModeBar: false, responsive: true}}).then(function() {{
            function triggerShake() {{
                chartDiv.classList.add('shake-active');
                setTimeout(function() {{
                    chartDiv.classList.remove('shake-active');
                }}, 2000);
            }}
            
            // Initial shake (staggered slightly to let it render)
            setTimeout(triggerShake, 1500);
            
            // Repeat every 30s
            setInterval(triggerShake, 30000);
        }});
    </script>
    """
    
    components.html(html_str, height=310)

def render_combined_monthly_chart(df_exp, df_rev, title):
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df_merged = pd.merge(df_exp, df_rev, on="MONTH_NAME", suffixes=("_EXP", "_REV"), how="outer")
    
    month_map = {m: i for i, m in enumerate(month_order)}
    df_merged['MONTH_IDX'] = df_merged['MONTH_NAME'].str.strip().str[:3].str.title().map(month_map)
    df_merged = df_merged.sort_values('MONTH_IDX').dropna(subset=['MONTH_IDX'])
    
    months = df_merged["MONTH_NAME"].astype(str).tolist()
    exp_values = df_merged["IMPLEMENTATION_EXP"].fillna(0).tolist()
    rev_values = df_merged["IMPLEMENTATION_REV"].fillna(0).tolist()
    
    fig = go.Figure()
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
    label_color = "#dcecff" if is_dark else "#1e293b" 
    grid_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
    annot_bg = "rgba(4, 18, 43, 0.8)" if is_dark else "rgba(255, 255, 255, 0.9)"
    annot_text_rev = "#00AD4E" if is_dark else "#059669"
    annot_text_exp = "#00A8E1" if is_dark else "#0284c7"

    if rev_values:
        r_max_idx = rev_values.index(max(rev_values))
        r_min_idx = rev_values.index(min(rev_values))
        
        fig.add_annotation(
            x=months[r_max_idx], y=rev_values[r_max_idx],
            text="Highest Rev", showarrow=True, arrowhead=2, arrowcolor=annot_text_rev,
            ax=0, ay=-40, font={"color": annot_text_rev, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_rev, borderwidth=1
        )
        fig.add_annotation(
            x=months[r_min_idx], y=rev_values[r_min_idx],
            text="Lowest Rev", showarrow=True, arrowhead=2, arrowcolor=annot_text_rev,
            ax=0, ay=40, font={"color": annot_text_rev, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_rev, borderwidth=1
        )
        
        fig.add_trace(go.Scatter(
            x=[months[r_max_idx], months[r_min_idx]], y=[rev_values[r_max_idx], rev_values[r_min_idx]], 
            mode='markers', marker={"size": 22, "color": "rgba(0, 173, 78, 0.155)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=[months[r_max_idx], months[r_min_idx]], y=[rev_values[r_max_idx], rev_values[r_min_idx]], 
            mode='markers', marker={"size": 15, "color": "rgba(0, 173, 78, 0.255)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=[months[r_max_idx], months[r_min_idx]], y=[rev_values[r_max_idx], rev_values[r_min_idx]], 
            mode='markers', marker={"size": 9, "color": "rgba(0, 173, 78, 0.455)", "line": {"color": "#00AD4E", "width": 2}},
            showlegend=False, hoverinfo='skip'
        ))

    if exp_values:
        e_max_idx = exp_values.index(max(exp_values))
        e_min_idx = exp_values.index(min(exp_values))

        fig.add_annotation(
            x=months[e_max_idx], y=exp_values[e_max_idx],
            text="Highest Exp", showarrow=True, arrowhead=2, arrowcolor=annot_text_exp,
            ax=0, ay=-40, font={"color": annot_text_exp, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_exp, borderwidth=1
        )
        fig.add_annotation(
            x=months[e_min_idx], y=exp_values[e_min_idx],
            text="Lowest Exp", showarrow=True, arrowhead=2, arrowcolor=annot_text_exp,
            ax=0, ay=40, font={"color": annot_text_exp, "size": 10, "family": "Arial Black"},
            bgcolor=annot_bg, bordercolor=annot_text_exp, borderwidth=1
        )
        
        fig.add_trace(go.Scatter(
            x=[months[e_max_idx], months[e_min_idx]], y=[exp_values[e_max_idx], exp_values[e_min_idx]], 
            mode='markers', marker={"size": 22, "color": "rgba(0, 168, 225, 0.155)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=[months[e_max_idx], months[e_min_idx]], y=[exp_values[e_max_idx], exp_values[e_min_idx]], 
            mode='markers', marker={"size": 15, "color": "rgba(0, 168, 225, 0.255)", "line": {"width": 0}},
            showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=[months[e_max_idx], months[e_min_idx]], y=[exp_values[e_max_idx], exp_values[e_min_idx]], 
            mode='markers', marker={"size": 9, "color": "rgba(0, 168, 225, 0.455)", "line": {"color": "#00A8E1", "width": 2}},
            showlegend=False, hoverinfo='skip'
        ))

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": text_color, "family": "Arial"}, "x": 0.05, "y": 0.95},
        height=300, margin={"l": 55, "r": 35, "t": 50, "b": 35},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 11},
        xaxis={"showline": False, "showgrid": False, "type": "category", "tickfont": {"color": label_color}},
        yaxis={"showline": False, "showgrid": True, "gridcolor": grid_color, "ticksuffix": " KHR", "tickformat": ".0s", "tickfont": {"color": label_color}},
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1, "font": {"color": label_color}},
        hovermode="x unified",
        transition={"duration": 1000, "easing": "cubic-in-out"}
    )
    
    rev_trace_ids = [0]
    exp_trace_ids = [1]
    rev_annot_ids = []
    exp_annot_ids = []
    
    trace_idx = 2
    annot_idx = 0
    if rev_values:
        rev_annot_ids.extend([annot_idx, annot_idx+1])
        annot_idx += 2
        rev_trace_ids.extend([trace_idx, trace_idx+1, trace_idx+2])
        trace_idx += 3
    if exp_values:
        exp_annot_ids.extend([annot_idx, annot_idx+1])
        annot_idx += 2
        exp_trace_ids.extend([trace_idx, trace_idx+1, trace_idx+2])
        trace_idx += 3

    fig_json = fig.to_json()
    
    import random
    import string
    uid = ''.join(random.choices(string.ascii_lowercase, k=4))
    chart_uid = f"plotly_monthly_{uid}"
    
    border_color = "rgba(92, 132, 184, 0.6)" if is_dark else "#e2e8f0"
    bg_style = "background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));" if is_dark else "background: #FFFFFF;"
    
    html_str = f"""
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; font-family: Arial, sans-serif; }}
        .plotly-anim-container {{
            border-radius: 12px;
            border: 1px solid {border_color};
            {bg_style}
            transition: border-color 0.3s ease;
            box-sizing: border-box;
            height: 300px;
            width: 100%;
        }}
        .plotly-anim-container:hover {{
            border-color: {"#20d6ff" if is_dark else "#3498dc"};
            box-shadow: 0 10px 20px rgba(32, 214, 255, 0.15);
        }}
        .trace {{
            transition: opacity 1.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div id="{chart_uid}" class="plotly-anim-container"></div>
    <script>
        var fig = {fig_json};
        var chartDiv = document.getElementById('{chart_uid}');
        
        Plotly.newPlot(chartDiv, fig.data, fig.layout, {{displayModeBar: false, responsive: true}}).then(function() {{
            
            function setTraceOpacity(expOp, revOp) {{
                Plotly.restyle(chartDiv, {{'opacity': expOp}}, {exp_trace_ids});
                Plotly.restyle(chartDiv, {{'opacity': revOp}}, {rev_trace_ids});
                
                var update = {{}};
                var revAnnots = {rev_annot_ids};
                for(var i=0; i<revAnnots.length; i++) update['annotations[' + revAnnots[i] + '].opacity'] = revOp;
                
                var expAnnots = {exp_annot_ids};
                for(var j=0; j<expAnnots.length; j++) update['annotations[' + expAnnots[j] + '].opacity'] = expOp;
                
                if (Object.keys(update).length > 0) {{
                    Plotly.relayout(chartDiv, update);
                }}
            }}

            function runAnim() {{
                // Stage 1: Focus on Expense (0s)
                setTraceOpacity(1, 0.15);

                // Stage 2: Focus on Revenue (2s)
                setTimeout(function() {{
                    setTraceOpacity(0.15, 1);
                }}, 2000); // 2s

                // Stage 3: Show Both (4s)
                setTimeout(function() {{
                    setTraceOpacity(1, 1);
                }}, 4000); // 4s
            }}

            // Start immediately
            runAnim();
            // Loop every 30 seconds
            setInterval(runAnim, 30000);
        }});
    </script>
    """
    components.html(html_str, height=310)

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
        text=exp_text, textposition='outside', cliponaxis=False,
        textfont={"color": bar_text_color_exp},
        hovertemplate='<b>%{y}</b><br>Expense: %{customdata:,.0f} KHR<extra></extra>',
        customdata=exp_vals
    ))
    fig.add_trace(go.Bar(
        y=qtrs, x=rev_vals, orientation='h', name='Revenue',
        marker={"color": '#00AD4E', "line": {"color": 'rgba(255,255,255,0.1)', "width": 1}},
        text=rev_text, textposition='outside', cliponaxis=False,
        textfont={"color": bar_text_color_rev},
        hovertemplate='<b>%{y}</b><br>Revenue: %{x:,.0f} KHR<extra></extra>'
    ))
    
    text_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b"
    grid_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
    center_bg = "rgba(4, 18, 43, 1.0)" if is_dark else "rgba(255, 255, 255, 0.9)"
    center_border = "rgba(32, 214, 255, 0.4)" if is_dark else "#e0e0e0"
    center_text = "#FFFFFF" if is_dark else "#1e293b"

    for q in qtrs:
        fig.add_annotation(
            x=0, y=q, text=q, showarrow=False,
            font={"color": center_text, "size": 13},
            bgcolor=center_bg, bordercolor=center_border,
            borderwidth=1, borderpad=5, opacity=1.0
        )
    
    max_val = max(max(rev_vals) if rev_vals else 0, max(exp_vals) if exp_vals else 0) * 1.5
    if max_val == 0: max_val = 1
    
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
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": text_color, "family": "Arial"}, "x": 0.05, "y": 0.95},
        height=300, margin={"l": 30, "r": 30, "t": 40, "b": 30},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 11},
        xaxis={
            "showline": False, "showgrid": True, "gridcolor": grid_color, 
            "range": [-max_val, max_val], "showticklabels": True, 
            "tickmode": "array", "tickvals": tick_vals, "ticktext": tick_text,
            "zeroline": True, "zerolinecolor": "rgba(128,128,128,0.4)", "zerolinewidth": 2,
            "tickfont": {"color": label_color}
        },
        yaxis={"showline": False, "showgrid": False, "type": "category", "showticklabels": False},
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1, "font": {"color": label_color}}
    )
    
    fig_json = fig.to_json()
    
    import random
    import string
    uid = ''.join(random.choices(string.ascii_lowercase, k=4))
    chart_uid = f"plotly_{uid}"
    
    border_color = "rgba(92, 132, 184, 0.6)" if is_dark else "#e2e8f0"
    bg_style = "background: linear-gradient(135deg, rgba(26, 45, 74, 0.4), rgba(4, 18, 43, 0.4));" if is_dark else "background: #FFFFFF;"
    
    html_str = f"""
    <style>
        body {{ margin: 0; padding: 0; background-color: transparent; overflow: hidden; font-family: Arial, sans-serif; }}
        .plotly-anim-container {{
            border-radius: 12px;
            border: 1px solid {border_color};
            {bg_style}
            transition: border-color 0.3s ease;
            box-sizing: border-box;
            height: 300px;
            width: 100%;
        }}
        .plotly-anim-container:hover {{
            border-color: {"#20d6ff" if is_dark else "#3498dc"};
            box-shadow: 0 10px 20px rgba(32, 214, 255, 0.15);
        }}
        .trace {{
            transition: opacity 1.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <div id="{chart_uid}" class="plotly-anim-container"></div>
    <script>
        var fig = {fig_json};
        var chartDiv = document.getElementById('{chart_uid}');
        
        Plotly.newPlot(chartDiv, fig.data, fig.layout, {{displayModeBar: false, responsive: true}}).then(function() {{
            
            function setTraceOpacity(expOp, revOp) {{
                Plotly.restyle(chartDiv, {{'opacity': [expOp, revOp]}}, [0, 1]);
            }}

            function runAnim() {{
                // Stage 1: Focus on Expense (0s)
                setTraceOpacity(1, 0.15);

                // Stage 2: Focus on Revenue (2s)
                setTimeout(function() {{
                    setTraceOpacity(0.15, 1);
                }}, 2000); // 2s

                // Stage 3: Show Both (4s)
                setTimeout(function() {{
                    setTraceOpacity(1, 1);
                }}, 4000); // 4s
            }}

            // Start immediately
            runAnim();
            // Loop every 30 seconds
            setInterval(runAnim, 30000);
        }});
    </script>
    """
    components.html(html_str, height=310)

def render_net_summary_chart(rev_summary, exp_summary, title):
    rev_val = rev_summary["Implementation"]
    exp_val = exp_summary["Implementation"]
    net_val = rev_val - exp_val
    
    categories = ['Revenue', 'Expense', 'Net']
    values = [rev_val, exp_val, net_val]
    colors = ['#00AD4E', '#00A8E1', '#1f6bff' if net_val >= 0 else '#ff9300']
    
    is_dark = st.session_state.theme == 'dark'
    data_label_color = 'white' if is_dark else '#1e293b'

    fig = go.Figure(data=[
        go.Bar(
            x=categories, y=values, marker_color=colors,
            marker_line=dict(width=1, color='rgba(255,255,255,0.2)'),
            text=[f"{v:,.0f} KHR" for v in values], textposition='outside', cliponaxis=False,
            textfont=dict(color=data_label_color, size=11),
            hovertemplate='<b>%{x}</b><br>Amount: %{y:,.0f} KHR<extra></extra>'
        )
    ])
    
    max_val = max(abs(rev_val), abs(exp_val), abs(net_val))
    y_range = [min(0, net_val) * 1.2, max_val * 1.2] if max_val > 0 else [0, 1]
    
    text_color = "#ffffff" if is_dark else "#1e293b"
    label_color = "#dcecff" if is_dark else "#1e293b"
    grid_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": text_color, "family": "Arial"}},
        height=300, margin={"l": 20, "r": 20, "t": 40, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": label_color, "size": 12},
        xaxis={"showline": False, "showgrid": False, "tickfont": {"color": label_color}},
        yaxis={
            "showline": False, "showgrid": True, "gridcolor": grid_color, 
            "ticksuffix": " KHR", "tickformat": ".0s", "range": y_range,
            "tickfont": {"color": label_color}
        },
        showlegend=False,
        transition={'duration': 1200, 'easing': 'cubic-in-out'}
    )
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
