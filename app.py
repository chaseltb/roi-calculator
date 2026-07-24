import json
import os
from urllib.parse import parse_qs

import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import plotly.graph_objects as go

# ── Brand Colors ──────────────────────────────────────────────────────────────
BG_PAGE   = "#070101"   # near-black, slight red tint
BG_CARD   = "#130202"   # dark card background
BG_INPUT  = "#0c0101"   # input fields
BORDER    = "#2e0805"   # subtle border
BORDER_HI = "#5a1208"   # highlighted border
RED_MAIN  = "#ff3428"   # vibrant red
RED_SEC   = "#be0a00"   # deep red
RED_GLOW  = "#ff3428"
WHITE     = "#ffffff"
TEXT_HI   = "#ffffff"
TEXT_MID  = "#c98080"   # mid-contrast label
TEXT_MUTE = "#7a4848"   # muted label
GREEN     = "#4ade80"   # bright green for ROI
GREEN_DIM = "rgba(74, 222, 128, 0.08)"

DEFAULT_CONFIG = {
    "product_name": "Etherea Website Platform",
    "timeline_months": 12,
    "tiers": [
        {"name": "Starter Package",    "cost": 809,  "limit": 100},
        {"name": "Growth Package",     "cost": 1237, "limit": 500},
        {"name": "Enterprise Package", "cost": 5000, "limit": 999999}
    ]
}

CONFIGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs")


def load_config(path):
    """Load a settings JSON file and merge it over DEFAULT_CONFIG.

    Missing keys fall back to defaults so partial config files still work.
    """
    with open(path, "r") as f:
        overrides = json.load(f)
    cfg = {**DEFAULT_CONFIG, **overrides}
    cfg["tiers"] = overrides.get("tiers", DEFAULT_CONFIG["tiers"])
    return cfg


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


CONFIG_FILE = os.environ.get("ROI_CONFIG_FILE")
INITIAL_CONFIG = load_config(CONFIG_FILE) if CONFIG_FILE else DEFAULT_CONFIG

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Etherea Labs — ROI Calculator",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

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

# ── Slider Row Helper ─────────────────────────────────────────────────────────
def slider_row(label, slider_id, val_id, min_v, max_v, step_v, default_v):
    return html.Div(
        style={"display": "flex", "flexDirection": "column", "gap": "10px"},
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline"},
                children=[
                    html.Span(label, style={"fontSize": "12px", "fontWeight": "600",
                                            "letterSpacing": "0.04em", "color": TEXT_MID,
                                            "textTransform": "uppercase"}),
                    html.Span(id=val_id, style={"fontSize": "16px", "fontWeight": "800", "color": WHITE})
                ]
            ),
            dcc.Slider(id=slider_id, min=min_v, max=max_v, step=step_v, value=default_v,
                       marks=None, tooltip={"always_visible": False})
        ]
    )

def parse_query(search):
    """Parse a dcc.Location `search` string (e.g. "?config=foo&embed=1") into a dict."""
    if not search:
        return {}
    qs = parse_qs(search.lstrip("?"))
    return {k: v[0] for k, v in qs.items()}


# ── Nav Bar ───────────────────────────────────────────────────────────────────
def nav_bar(current_path, embed=False):
    if embed:
        return None
    is_config = current_path == "/config"
    return html.Div(
        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center",
               "padding": "1.1rem 2rem", "borderBottom": f"1px solid {BORDER}",
               "marginBottom": "0"},
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "10px"},
                children=[
                    html.Div(
                        "E",
                        style={"width": "30px", "height": "30px", "borderRadius": "7px",
                               "background": f"linear-gradient(135deg, {RED_MAIN} 0%, {RED_SEC} 100%)",
                               "display": "flex", "alignItems": "center", "justifyContent": "center",
                               "fontSize": "15px", "fontWeight": "800", "color": WHITE,
                               "flexShrink": "0"}
                    ),
                    html.Span("Etherea Labs",
                              style={"fontSize": "14px", "fontWeight": "700",
                                     "letterSpacing": "-0.01em", "color": WHITE})
                ]
            ),
            dcc.Link(
                "← Dashboard" if is_config else "⚙ Configure",
                href="/" if is_config else "/config",
                style={"color": TEXT_MUTE, "fontSize": "12px", "fontWeight": "600",
                       "textDecoration": "none", "letterSpacing": "0.02em"}
            )
        ]
    )

# ── Home Layout ───────────────────────────────────────────────────────────────
def home_layout(embed=False):
    card = lambda extra={}: {
        "background": BG_CARD,
        "border": f"1px solid {BORDER}",
        "borderRadius": "14px",
        **extra
    }

    return html.Div(
        children=[
            nav_bar("/", embed=embed),
            # Bento grid container
            html.Div(
                style={"padding": "0.75rem" if embed else "1.5rem 1.75rem 2rem",
                       "maxWidth": "1280px",
                       "margin": "0 auto"},
                children=[
                    # Page label
                    html.Div(
                        id="main-title",
                        style={"fontSize": "12px", "fontWeight": "700", "letterSpacing": "0.12em",
                               "textTransform": "uppercase", "color": TEXT_MUTE,
                               "marginBottom": "1.25rem"}
                    ),

                    # ── Bento Grid ───────────────────────────────────────────
                    html.Div(
                        id="bento-grid",
                        style={
                            "display": "grid",
                            # cols: fixed inputs | flex | flex
                            "gridTemplateColumns": "340px 1fr 1fr",
                            "gridTemplateRows": "auto auto 1fr",
                            "gridTemplateAreas": (
                                '"inputs roi     payback"'
                                '"inputs profit  profit "'
                                '"inputs chart   chart  "'
                            ),
                            "gap": "1rem",
                            "alignItems": "stretch",
                        },
                        children=[

                            # ── INPUTS (left column, spans all rows) ─────────
                            html.Div(
                                style={"gridArea": "inputs", **card(),
                                       "padding": "1.75rem",
                                       "display": "flex", "flexDirection": "column",
                                       "gap": "0"},
                                children=[
                                    # Section: Your Business
                                    html.Div("Your Business",
                                             style={"fontSize": "10px", "fontWeight": "700",
                                                    "letterSpacing": "0.12em", "textTransform": "uppercase",
                                                    "color": TEXT_MUTE, "marginBottom": "1.5rem"}),

                                    html.Div(
                                        style={"display": "flex", "flexDirection": "column", "gap": "1.5rem"},
                                        children=[
                                            slider_row("Sales Per Year", "units-slider",
                                                       "units-slider-val", 10, 5000, 10, 150),
                                            slider_row("Profit Per Sale", "profit-slider",
                                                       "profit-slider-val", 10, 5000, 10, 250),
                                        ]
                                    ),

                                    # Divider
                                    html.Hr(style={"border": "none", "borderTop": f"1px solid {BORDER}",
                                                   "margin": "1.75rem 0"}),

                                    # Section: Projected Gains
                                    html.Div("Projected Gains",
                                             style={"fontSize": "10px", "fontWeight": "700",
                                                    "letterSpacing": "0.12em", "textTransform": "uppercase",
                                                    "color": TEXT_MUTE, "marginBottom": "1.5rem"}),

                                    html.Div(
                                        style={"display": "flex", "flexDirection": "column", "gap": "1.5rem"},
                                        children=[
                                            slider_row("Conversion Boost", "conversion-slider",
                                                       "conversion-slider-val", 5, 100, 5, 25),
                                            slider_row("SEO Traffic Growth", "traffic-slider",
                                                       "traffic-slider-val", 0, 100, 5, 20),
                                        ]
                                    ),

                                    # Spacer
                                    html.Div(style={"flex": "1"}),

                                    # Package strip at bottom of inputs
                                    html.Div(
                                        style={"borderTop": f"1px solid {BORDER}",
                                               "paddingTop": "1.25rem", "marginTop": "1.5rem",
                                               "display": "flex", "justifyContent": "space-between",
                                               "alignItems": "flex-end"},
                                        children=[
                                            html.Div([
                                                html.Div("Package",
                                                         style={"fontSize": "10px", "fontWeight": "700",
                                                                "letterSpacing": "0.1em", "textTransform": "uppercase",
                                                                "color": TEXT_MUTE, "marginBottom": "4px"}),
                                                html.Div(id="tier-name-val",
                                                         style={"fontSize": "15px", "fontWeight": "700",
                                                                "color": WHITE})
                                            ]),
                                            html.Div([
                                                html.Div("Investment",
                                                         style={"fontSize": "10px", "fontWeight": "700",
                                                                "letterSpacing": "0.1em", "textTransform": "uppercase",
                                                                "color": TEXT_MUTE, "marginBottom": "4px",
                                                                "textAlign": "right"}),
                                                html.Div(id="tier-cost-val",
                                                         style={"fontSize": "20px", "fontWeight": "800",
                                                                "color": RED_MAIN, "letterSpacing": "-0.02em"})
                                            ])
                                        ]
                                    )
                                ]
                            ),

                            # ── ROI % (top-middle) ───────────────────────────
                            html.Div(
                                style={"gridArea": "roi", **card(),
                                       "padding": "1.5rem 1.75rem",
                                       "display": "flex", "flexDirection": "column",
                                       "gap": "8px"},
                                children=[
                                    html.Div("Return on Investment",
                                             style={"fontSize": "10px", "fontWeight": "700",
                                                    "letterSpacing": "0.12em", "textTransform": "uppercase",
                                                    "color": TEXT_MUTE}),
                                    html.Div(
                                        style={"display": "flex", "alignItems": "baseline", "gap": "4px"},
                                        children=[
                                            html.Span(id="metric-roi",
                                                      style={"fontSize": "52px", "fontWeight": "900",
                                                             "color": GREEN, "letterSpacing": "-0.05em",
                                                             "lineHeight": "1"}),
                                            html.Span("%",
                                                      style={"fontSize": "26px", "fontWeight": "700",
                                                             "color": GREEN, "opacity": "0.7"})
                                        ]
                                    )
                                ]
                            ),

                            # ── PAYBACK (top-right) ──────────────────────────
                            html.Div(
                                style={"gridArea": "payback", **card(),
                                       "padding": "1.5rem 1.75rem",
                                       "display": "flex", "flexDirection": "column",
                                       "gap": "8px"},
                                children=[
                                    html.Div("Payback Period",
                                             style={"fontSize": "10px", "fontWeight": "700",
                                                    "letterSpacing": "0.12em", "textTransform": "uppercase",
                                                    "color": TEXT_MUTE}),
                                    html.Div(
                                        id="metric-payback",
                                        style={"fontSize": "52px", "fontWeight": "900",
                                               "color": WHITE, "letterSpacing": "-0.05em",
                                               "lineHeight": "1"}
                                    )
                                ]
                            ),

                            # ── EXTRA PROFIT — hero card (middle row, spans 2 cols) ──
                            html.Div(
                                style={
                                    "gridArea": "profit",
                                    "background": f"linear-gradient(135deg, {RED_SEC} 0%, #900600 100%)",
                                    "border": f"1px solid {BORDER_HI}",
                                    "borderRadius": "14px",
                                    "padding": "2rem 2.25rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "justifyContent": "center",
                                    "gap": "10px",
                                },
                                children=[
                                    html.Div("Extra Annual Profit",
                                             style={"fontSize": "10px", "fontWeight": "700",
                                                    "letterSpacing": "0.12em", "textTransform": "uppercase",
                                                    "color": "rgba(255,255,255,0.55)"}),
                                    html.Div(
                                        style={"display": "flex", "alignItems": "baseline", "gap": "4px"},
                                        children=[
                                            html.Span("$",
                                                      style={"fontSize": "32px", "fontWeight": "700",
                                                             "color": "rgba(255,255,255,0.65)"}),
                                            html.Span(id="metric-net-profit",
                                                      style={"fontSize": "72px", "fontWeight": "900",
                                                             "color": WHITE, "letterSpacing": "-0.05em",
                                                             "lineHeight": "1"})
                                        ]
                                    )
                                ]
                            ),

                            # ── CHART (bottom row, spans 2 cols) ─────────────
                            html.Div(
                                style={"gridArea": "chart", **card(),
                                       "padding": "1.5rem 1.75rem",
                                       "display": "flex", "flexDirection": "column",
                                       "gap": "1rem"},
                                children=[
                                    html.Div(
                                        style={"display": "flex", "justifyContent": "space-between",
                                               "alignItems": "center"},
                                        children=[
                                            html.Div("Cumulative Return",
                                                     style={"fontSize": "12px", "fontWeight": "700",
                                                            "color": WHITE, "letterSpacing": "-0.01em"}),
                                            html.Span(id="timeline-badge",
                                                      style={"fontSize": "10px", "color": TEXT_MUTE,
                                                             "background": "rgba(255,255,255,0.04)",
                                                             "padding": "3px 8px", "borderRadius": "4px",
                                                             "fontWeight": "700", "letterSpacing": "0.06em",
                                                             "textTransform": "uppercase"})
                                        ]
                                    ),
                                    dcc.Graph(id="cumulative-chart",
                                              config={"displayModeBar": False},
                                              style={"height": "220px", "minHeight": "180px"})
                                ]
                            ),
                        ]
                    )
                ]
            )
        ]
    )

# ── Config Layout ─────────────────────────────────────────────────────────────
def config_layout():
    input_style = {
        "background": BG_INPUT, "border": f"1px solid {BORDER}", "borderRadius": "8px",
        "color": WHITE, "padding": "10px 12px", "width": "100%", "boxSizing": "border-box",
        "fontSize": "14px", "outline": "none"
    }
    lbl = {"fontSize": "10px", "fontWeight": "700", "color": TEXT_MUTE,
           "display": "block", "marginBottom": "6px", "letterSpacing": "0.1em",
           "textTransform": "uppercase"}

    def field(label, inp):
        return html.Div([html.Label(label, style=lbl), inp])

    return html.Div(children=[
        nav_bar("/config"),
        html.Div(
            style={"maxWidth": "720px", "margin": "0 auto", "padding": "2rem 2rem 4rem"},
            children=[
                html.H1("Configure Parameters",
                        style={"fontSize": "22px", "fontWeight": "800",
                               "letterSpacing": "-0.03em", "margin": "0 0 2rem 0"}),
                html.Div(
                    style={"background": BG_CARD, "border": f"1px solid {BORDER}",
                           "borderRadius": "14px", "padding": "2rem",
                           "display": "flex", "flexDirection": "column", "gap": "1.75rem"},
                    children=[
                        html.Div(
                            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1.25rem"},
                            children=[
                                field("Product / Service Name",
                                      dcc.Input(id="cfg-product-name", type="text", style=input_style)),
                                field("Timeline (Months)",
                                      dcc.Input(id="cfg-timeline", type="number", min=1, max=120, style=input_style))
                            ]
                        ),
                        html.Hr(style={"border": "none", "borderTop": f"1px solid {BORDER}", "margin": "0"}),
                        html.Div("Pricing Tiers",
                                 style={"fontSize": "12px", "fontWeight": "700", "color": WHITE}),
                        *[
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1.2fr", "gap": "1.25rem"},
                                children=[
                                    field(f"Tier {i} Name",
                                          dcc.Input(id=f"cfg-t{i}-name", type="text", style=input_style)),
                                    field("Cost ($)",
                                          dcc.Input(id=f"cfg-t{i}-cost", type="number", style=input_style)),
                                    field("Sales Volume Limit",
                                          dcc.Input(
                                              id=f"cfg-t{i}-limit",
                                              **({"type": "number"} if i < 3 else
                                                 {"value": "Unlimited", "disabled": True}),
                                              style={**input_style,
                                                     **({"opacity": "0.35", "cursor": "not-allowed"} if i == 3 else {})}
                                          ))
                                ]
                            )
                            for i in [1, 2, 3]
                        ],
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between",
                                   "alignItems": "center", "marginTop": "0.25rem"},
                            children=[
                                html.Button("Reset to Defaults", id="btn-reset", n_clicks=0,
                                            style={"background": "transparent", "border": f"1px solid {BORDER}",
                                                   "color": TEXT_MID, "padding": "9px 18px",
                                                   "borderRadius": "8px", "fontSize": "13px",
                                                   "fontWeight": "600", "cursor": "pointer"}),
                                html.Button("Save Configuration", id="btn-save", n_clicks=0,
                                            style={"background": f"linear-gradient(135deg, {RED_MAIN} 0%, {RED_SEC} 100%)",
                                                   "border": "none", "color": WHITE, "padding": "9px 22px",
                                                   "borderRadius": "8px", "fontSize": "13px",
                                                   "fontWeight": "700", "cursor": "pointer"})
                            ]
                        ),
                        html.Div(id="cfg-status-message",
                                 style={"fontSize": "12px", "textAlign": "right", "fontWeight": "500"})
                    ]
                )
            ]
        )
    ])

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
    State("config-store", "data"),
    prevent_initial_call=True
)
def manage_config(save_n, reset_n, name, timeline,
                  t1n, t1c, t1l, t2n, t2c, t2l, t3n, t3c, store):
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

        cfg = {
            "product_name": name,
            "timeline_months": timeline_val,
            "tiers": [
                {"name": t1n or "Starter Package",    "cost": t1_cost, "limit": t1_limit},
                {"name": t2n or "Growth Package",     "cost": t2_cost, "limit": t2_limit},
                {"name": t3n or "Enterprise Package", "cost": t3_cost, "limit": 999999}
            ]
        }
        return cfg, "Saved.", {**base_style, "color": GREEN}
    return store or DEFAULT_CONFIG, "", {}

@callback(
    Output("cfg-product-name", "value"), Output("cfg-timeline", "value"),
    Output("cfg-t1-name", "value"), Output("cfg-t1-cost", "value"), Output("cfg-t1-limit", "value"),
    Output("cfg-t2-name", "value"), Output("cfg-t2-cost", "value"), Output("cfg-t2-limit", "value"),
    Output("cfg-t3-name", "value"), Output("cfg-t3-cost", "value"),
    Input("url", "pathname"), State("config-store", "data")
)
def populate_config(pathname, store):
    if pathname != "/config":
        return [dash.no_update] * 10
    cfg = store or DEFAULT_CONFIG
    t = cfg["tiers"]
    return (cfg["product_name"], cfg["timeline_months"],
            t[0]["name"], t[0]["cost"], t[0]["limit"],
            t[1]["name"], t[1]["cost"], t[1]["limit"],
            t[2]["name"], t[2]["cost"])

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
    Input("units-slider", "value"),
    Input("profit-slider", "value"),
    Input("conversion-slider", "value"),
    Input("traffic-slider", "value"),
    Input("config-store", "data"),
    Input("url", "pathname")
)
def update_calculator(units_val, profit_val, conv_val, traffic_val, config_data, pathname):
    if pathname == "/config":
        return [dash.no_update] * 12

    cfg = config_data or DEFAULT_CONFIG
    timeline = cfg["timeline_months"]
    tiers = cfg["tiers"]

    active_tier = tiers[0]
    for tier in tiers:
        if units_val <= tier["limit"]:
            active_tier = tier
            break

    tier_cost = active_tier["cost"]
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
        fig
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
# "https://etherealabs.com https://client-site.com" — defaults to "*" for demos.
@app.server.after_request
def _allow_embedding(response):
    response.headers.pop("X-Frame-Options", None)
    ancestors = os.environ.get("ROI_FRAME_ANCESTORS", "*")
    response.headers["Content-Security-Policy"] = f"frame-ancestors {ancestors}"
    return response


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("ROI_PORT", 4006)))
