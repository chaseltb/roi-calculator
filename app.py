import json
import os
from urllib.parse import parse_qs

import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import plotly.graph_objects as go

from theme import (
    DEFAULT_CONFIG, INITIAL_CONFIG, CONFIGS_DIR, load_config,
    BG_PAGE, BG_CARD, BG_INPUT, BORDER, BORDER_HI,
    RED_MAIN, RED_SEC, RED_GLOW, WHITE, TEXT_HI, TEXT_MID, TEXT_MUTE,
    GREEN, GREEN_DIM,
    BRAND_NAME, APP_TITLE, BRAND_INITIALS, BRAND_SITE,
)
from layout import config_layout, home_layout




def load_config_by_slug(slug):
    """Resolve a `?config=slug` query param to configs/<slug>.json.

    Only bare filenames (no path separators / traversal) are accepted, and the
    resolved path must stay inside CONFIGS_DIR. Returns None if the slug is
    invalid or the file doesn't exist, so callers can fall back safely.
    """
    if not slug or "/" in slug or "\\" in slug or ".." in slug:
        return None
    path = os.path.join(CONFIGS_DIR, f"{slug}.json")
    if not os.path.abspath(path).startswith(CONFIGS_DIR) or not os.path.isfile(path):
        return None
    try:
        return load_config(path)
    except (json.JSONDecodeError, OSError):
        return None



app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title=APP_TITLE,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # exposed for WSGI servers, e.g. `gunicorn app:server`

app.layout = html.Div(
    style={"background": BG_PAGE, "minHeight": "100vh", "margin": "0",
           "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
           "color": WHITE},
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="config-store", data=INITIAL_CONFIG, storage_type="session"),
        html.Div(id="page-content")
    ]
)

def parse_query(search):
    """Parse a dcc.Location `search` string (e.g. "?config=foo&embed=1") into a dict."""
    if not search:
        return {}
    qs = parse_qs(search.lstrip("?"))
    return {k: v[0] for k, v in qs.items()}



# ── Routing ───────────────────────────────────────────────────────────────────
@callback(
    Output("page-content", "children"),
    Input("url", "pathname"), Input("url", "search")
)
def render_route(pathname, search):
    query = parse_query(search)
    embed = query.get("embed") in ("1", "true")
    if pathname == "/config":
        return config_layout()
    return home_layout(embed=embed)


# Seeds config-store from `?config=<slug>` on first load, e.g. for embeds like
# <iframe src="https://.../?config=marketing_agency&embed=1">. Falls back to
# whatever is already in the session store (or DEFAULT_CONFIG) if the slug is
# missing/invalid, so this never clobbers a config saved via the /config page.
@callback(
    Output("config-store", "data", allow_duplicate=True),
    Input("url", "search"),
    State("config-store", "data"),
    prevent_initial_call="initial_duplicate"
)
def seed_config_from_query(search, store):
    query = parse_query(search)
    cfg = load_config_by_slug(query.get("config"))
    return cfg if cfg is not None else (store or DEFAULT_CONFIG)

# ── Config Callbacks ──────────────────────────────────────────────────────────
@callback(
    Output("config-store", "data", allow_duplicate=True),
    Output("cfg-status-message", "children"),
    Output("cfg-status-message", "style"),
    Input("btn-save", "n_clicks"), Input("btn-reset", "n_clicks"),
    State("cfg-product-name", "value"), State("cfg-timeline", "value"),
    State("cfg-t1-name", "value"), State("cfg-t1-cost", "value"), State("cfg-t1-limit", "value"),
    State("cfg-t2-name", "value"), State("cfg-t2-cost", "value"), State("cfg-t2-limit", "value"),
    State("cfg-t3-name", "value"), State("cfg-t3-cost", "value"),
    State("cfg-units-label", "value"), State("cfg-profit-label", "value"),
    State("cfg-conversion-label", "value"), State("cfg-traffic-label", "value"),
    State("cfg-additional-sales-mode", "value"),
    State("config-store", "data"),
    prevent_initial_call=True
)
def manage_config(save_n, reset_n, name, timeline,
                  t1n, t1c, t1l, t2n, t2c, t2l, t3n, t3c,
                  u_lbl, p_lbl, c_lbl, tr_lbl, asm_val, store):
    base_style = {"textAlign": "right", "fontSize": "12px", "fontWeight": "600"}
    triggered = ctx.triggered_id
    if triggered == "btn-reset":
        return DEFAULT_CONFIG, "Reset to defaults.", {**base_style, "color": TEXT_MID}
    if triggered == "btn-save":
        if not name or timeline is None:
            return store, "Fill in all fields.", {**base_style, "color": RED_MAIN}
        try:
            timeline_val = int(timeline)
            t1_cost, t2_cost, t3_cost = float(t1c or 0), float(t2c or 0), float(t3c or 0)
            t1_limit, t2_limit = int(t1l or 100), int(t2l or 500)
        except (TypeError, ValueError):
            return store, "Costs, limits, and timeline must be numbers.", {**base_style, "color": RED_MAIN}

        if not (1 <= timeline_val <= 120):
            return store, "Timeline must be between 1 and 120 months.", {**base_style, "color": RED_MAIN}
        if min(t1_cost, t2_cost, t3_cost) < 0:
            return store, "Costs can't be negative.", {**base_style, "color": RED_MAIN}
        if t1_limit <= 0 or t2_limit <= t1_limit:
            return store, "Tier 2's volume limit must exceed Tier 1's.", {**base_style, "color": RED_MAIN}

        existing_brand = (store or DEFAULT_CONFIG).get("brand", DEFAULT_CONFIG["brand"])
        existing_colors = (store or DEFAULT_CONFIG).get("colors", DEFAULT_CONFIG["colors"])

        cfg = {
            "product_name": name,
            "timeline_months": timeline_val,
            "tiers": [
                {"name": t1n or "Starter Package",    "cost": t1_cost, "limit": t1_limit},
                {"name": t2n or "Growth Package",     "cost": t2_cost, "limit": t2_limit},
                {"name": t3n or "Enterprise Package", "cost": t3_cost, "limit": 999999}
            ],
            "brand": existing_brand,
            "colors": existing_colors,
            "sliders": {
                "units_label":      u_lbl.strip() if u_lbl and u_lbl.strip() else DEFAULT_CONFIG["sliders"]["units_label"],
                "profit_label":     p_lbl.strip() if p_lbl and p_lbl.strip() else DEFAULT_CONFIG["sliders"]["profit_label"],
                "conversion_label": c_lbl.strip() if c_lbl and c_lbl.strip() else DEFAULT_CONFIG["sliders"]["conversion_label"],
                "traffic_label":    tr_lbl.strip() if tr_lbl and tr_lbl.strip() else DEFAULT_CONFIG["sliders"]["traffic_label"],
            },
            "additional_sales_mode": "enabled" in (asm_val or [])
        }
        return cfg, "Saved.", {**base_style, "color": GREEN}
    return store or DEFAULT_CONFIG, "", {}

@callback(
    Output("cfg-product-name", "value"), Output("cfg-timeline", "value"),
    Output("cfg-t1-name", "value"), Output("cfg-t1-cost", "value"), Output("cfg-t1-limit", "value"),
    Output("cfg-t2-name", "value"), Output("cfg-t2-cost", "value"), Output("cfg-t2-limit", "value"),
    Output("cfg-t3-name", "value"), Output("cfg-t3-cost", "value"),
    Output("cfg-units-label", "value"), Output("cfg-profit-label", "value"),
    Output("cfg-conversion-label", "value"), Output("cfg-traffic-label", "value"),
    Output("cfg-additional-sales-mode", "value"),
    Input("url", "pathname"), State("config-store", "data")
)
def populate_config(pathname, store):
    if pathname != "/config":
        return [dash.no_update] * 15
    cfg = store or DEFAULT_CONFIG
    t = cfg.get("tiers", DEFAULT_CONFIG["tiers"])
    sliders = cfg.get("sliders", DEFAULT_CONFIG["sliders"])
    asm = ["enabled"] if cfg.get("additional_sales_mode", False) else []
    return (cfg["product_name"], cfg["timeline_months"],
            t[0]["name"], t[0]["cost"], t[0]["limit"],
            t[1]["name"], t[1]["cost"], t[1]["limit"],
            t[2]["name"], t[2]["cost"],
            sliders.get("units_label", ""),
            sliders.get("profit_label", ""),
            sliders.get("conversion_label", ""),
            sliders.get("traffic_label", ""),
            asm)

# ── Calculator Engine ─────────────────────────────────────────────────────────
@callback(
    Output("main-title", "children"),
    Output("units-slider-val", "children"),
    Output("profit-slider-val", "children"),
    Output("conversion-slider-val", "children"),
    Output("traffic-slider-val", "children"),
    Output("tier-name-val", "children"),
    Output("tier-cost-val", "children"),
    Output("metric-net-profit", "children"),
    Output("metric-roi", "children"),
    Output("metric-payback", "children"),
    Output("timeline-badge", "children"),
    Output("cumulative-chart", "figure"),
    Output("units-label", "children"),
    Output("profit-label", "children"),
    Output("conversion-label", "children"),
    Output("traffic-label", "children"),
    Output("projected-gains-container", "style"),
    Input("units-slider", "value"),
    Input("profit-slider", "value"),
    Input("conversion-slider", "value"),
    Input("traffic-slider", "value"),
    Input("config-store", "data"),
    Input("url", "pathname")
)
def update_calculator(units_val, profit_val, conv_val, traffic_val, config_data, pathname):
    if pathname == "/config":
        return [dash.no_update] * 17

    cfg = config_data or DEFAULT_CONFIG
    timeline = cfg.get("timeline_months", 12)
    tiers = cfg.get("tiers", DEFAULT_CONFIG["tiers"])
    additional_sales_mode = cfg.get("additional_sales_mode", False)
    sliders_cfg = cfg.get("sliders", DEFAULT_CONFIG["sliders"])

    # Resolve dynamic slider labels based on mode and overrides
    default_units_lbl = "Additional Sales Per Year" if additional_sales_mode else "Current Sales Per Year"
    units_lbl = sliders_cfg.get("units_label") or default_units_lbl
    profit_lbl = sliders_cfg.get("profit_label") or "Profit Per Sale"
    conv_lbl = sliders_cfg.get("conversion_label") or "Conversion Boost"
    traffic_lbl = sliders_cfg.get("traffic_label") or "SEO Traffic Growth"

    active_tier = tiers[0]
    for tier in tiers:
        if units_val <= tier["limit"]:
            active_tier = tier
            break

    tier_cost = active_tier["cost"]

    if additional_sales_mode:
        # Simple logic: units_val is directly the additional sales per year generated!
        incremental_annual = units_val * profit_val
    else:
        # Current sales mode: multiplier logic on current baseline sales
        new_units = round(units_val * (1 + conv_val / 100) * (1 + traffic_val / 100))
        incremental_annual = (new_units - units_val) * profit_val

    net_benefit = incremental_annual * (timeline / 12) - tier_cost
    roi = (net_benefit / tier_cost * 100) if tier_cost > 0 else 0

    payback_mo = (tier_cost / (incremental_annual / 12)) if incremental_annual > 0 else float("inf")
    if payback_mo == float("inf"):
        payback_str = "—"
    elif payback_mo < 1:
        payback_str = "< 1 mo"
    else:
        payback_str = f"{payback_mo:.1f} mo"

    # Chart
    months = list(range(timeline + 1))
    cash_flow = [-tier_cost + (incremental_annual / 12) * m for m in months]

    breakeven_mo = next((i for i, cf in enumerate(cash_flow) if cf >= 0), None)

    fig = go.Figure()

    # Cost zone (below zero)
    fig.add_trace(go.Scatter(
        x=months, y=[min(cf, 0) for cf in cash_flow],
        mode="lines", line=dict(width=0),
        fill="tozeroy", fillcolor="rgba(190, 10, 0, 0.18)",
        showlegend=False, hoverinfo="skip"
    ))
    # Profit zone (above zero)
    fig.add_trace(go.Scatter(
        x=months, y=[max(cf, 0) for cf in cash_flow],
        mode="lines", line=dict(width=0),
        fill="tozeroy", fillcolor="rgba(74, 222, 128, 0.08)",
        showlegend=False, hoverinfo="skip"
    ))
    # Main line
    fig.add_trace(go.Scatter(
        x=months, y=cash_flow, mode="lines",
        line=dict(color=RED_MAIN, width=2.5),
        hovertemplate="Month %{x}: $%{y:,.0f}<extra></extra>"
    ))

    if breakeven_mo is not None:
        y_range_span = max(cash_flow) - min(cash_flow)
        fig.add_shape(type="line",
                      x0=breakeven_mo, y0=min(cash_flow),
                      x1=breakeven_mo, y1=max(cash_flow),
                      line=dict(color="rgba(255,255,255,0.12)", width=1, dash="dot"))
        fig.add_annotation(
            x=breakeven_mo, y=min(cash_flow) + y_range_span * 0.05,
            text="break even", showarrow=False,
            font=dict(color="rgba(255,255,255,0.28)", size=9, family="Inter"),
            xanchor="left"
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=4, b=0),
        font=dict(family="Inter, sans-serif", color=TEXT_MUTE, size=10),
        xaxis=dict(showgrid=False, tickmode="linear", dtick=max(1, timeline // 6),
                   tickfont=dict(color=TEXT_MUTE, size=10),
                   title=dict(text="Month", font=dict(size=10, color=TEXT_MUTE), standoff=4)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   tickfont=dict(color=TEXT_MUTE, size=10),
                   tickprefix="$", tickformat=",", zeroline=False),
        showlegend=False, hovermode="x unified"
    )

    def fmt(v):
        if abs(v) >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        if abs(v) >= 10_000:
            return f"{v / 1_000:.0f}K"
        return f"{round(v):,}"

    return (
        f"{cfg['product_name']} — ROI Calculator",
        f"{units_val:,} / yr",
        f"${profit_val:,}",
        f"+{conv_val}%",
        f"+{traffic_val}%",
        active_tier["name"],
        f"${tier_cost:,.0f}",
        fmt(net_benefit),
        f"{round(roi):,}",
        payback_str,
        f"{timeline}-Month View",
        fig,
        units_lbl,
        profit_lbl,
        conv_lbl,
        traffic_lbl,
        {"display": "none"} if additional_sales_mode else {}
    )

# ── Index HTML ────────────────────────────────────────────────────────────────
app.index_string = f"""<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ background-color: {BG_PAGE}; margin: 0; }}

            /* Sliders */
            .rc-slider-rail  {{ background: {BORDER} !important; height: 3px !important; border-radius: 2px !important; }}
            .rc-slider-track {{ background: {RED_MAIN} !important; height: 3px !important; border-radius: 2px !important; }}
            .rc-slider-handle {{
                border: 2px solid {RED_MAIN} !important;
                background: {BG_PAGE} !important;
                width: 15px !important; height: 15px !important;
                margin-top: -6px !important; opacity: 1 !important; box-shadow: none !important;
            }}
            .rc-slider-handle:hover,
            .rc-slider-handle:active {{
                background: {RED_MAIN} !important;
                box-shadow: 0 0 10px rgba(255, 52, 40, 0.45) !important;
            }}

            /* Responsive: stack on narrow screens */
            @media (max-width: 900px) {{
                #bento-grid {{
                    grid-template-columns: 1fr !important;
                    grid-template-rows: auto !important;
                    grid-template-areas:
                        "inputs"
                        "profit"
                        "roi"
                        "payback"
                        "chart" !important;
                }}
            }}

            /* Input focus */
            input:focus {{ border-color: {BORDER_HI} !important; outline: none !important; }}
            input[type="number"]::-webkit-inner-spin-button {{ opacity: 0.25; }}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer>
        <script>
            // Auto-report content height to a parent window when embedded in an
            // <iframe>, so the host page can size the iframe without scrollbars.
            (function () {{
                if (window.self === window.top) return;
                var lastHeight = 0;
                function reportHeight() {{
                    var height = document.documentElement.scrollHeight;
                    if (height !== lastHeight) {{
                        lastHeight = height;
                        window.parent.postMessage({{type: "roi-calculator:height", height: height}}, "*");
                    }}
                }}
                new MutationObserver(reportHeight).observe(document.body, {{
                    childList: true, subtree: true, attributes: true
                }});
                window.addEventListener("resize", reportHeight);
                setTimeout(reportHeight, 300);
            }})();
        </script>
    </body>
</html>"""

# Allow this app to be framed by other sites (needed to embed it as an
# <iframe>). Restrict via ROI_FRAME_ANCESTORS in production, e.g.
# "https://brand-site.com https://client-site.com" — defaults to "*" for demos.
@app.server.after_request
def _allow_embedding(response):
    response.headers.pop("X-Frame-Options", None)
    ancestors = os.environ.get("ROI_FRAME_ANCESTORS", "*")
    response.headers["Content-Security-Policy"] = f"frame-ancestors {ancestors}"
    return response


if __name__ == "__main__":
    app.run(debug=False, port=int(os.environ.get("ROI_PORT", 4006)))
