import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import plotly.graph_objects as go

# ── Brand Colors & Style Constants (Original Etherea Labs Reds) ──────────────
BG_DEEP   = "#1a0503"  # Deep red-black page background
BG_CARD   = "#550a04"  # Warm dark red card background
BORDER    = "#6e1208"  # Original burgundy border
RED_MAIN  = "#ff120a"  # Original vibrant cherry red
RED_SEC   = "#960502"  # Original secondary dark red
WHITE     = "#ffffff"  # Pure white
TEXT_MID  = "#c07070"  # Soft pink-red text
TEXT_MUTE = "#a07070"  # Muted warm red-grey

DEFAULT_CONFIG = {
    "product_name": "Etherea Website Platform",
    "timeline_months": 12,
    "tiers": [
        {"name": "Starter Package", "cost": 809, "limit": 100},
        {"name": "Growth Package", "cost": 1237, "limit": 500},
        {"name": "Enterprise Package", "cost": 5000, "limit": 999999}
    ]
}

# Initialize Dash App
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Etherea Labs — Value-Based ROI Calculator",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# Custom layout shell
app.layout = html.Div(
    style={
        "background": BG_DEEP,
        "minHeight": "100vh",
        "margin": "0",
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "color": WHITE,
    },
    children=[
        dcc.Location(id="url", refresh=False),
        # Session store for configuration data
        dcc.Store(id="config-store", data=DEFAULT_CONFIG, storage_type="session"),
        html.Div(id="page-content")
    ]
)

# ── Reusable Component Helpers ──────────────────────────────────────────────
def metric_card(label, value_id, suffix="", prefix="", value_color=WHITE):
    return html.Div(
        style={
            "background": BG_CARD,
            "border": f"1px solid {BORDER}",
            "borderRadius": "12px",
            "padding": "1.25rem",
            "display": "flex",
            "flexDirection": "column",
            "gap": "6px",
            "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.2)"
        },
        children=[
            html.Div(label, style={"fontSize": "11px", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": TEXT_MUTE, "fontWeight": "600"}),
            html.Div(
                children=[
                    html.Span(prefix, style={"fontSize": "18px", "color": TEXT_MID, "marginRight": "2px"}),
                    html.Span(id=value_id, style={"fontSize": "28px", "fontWeight": "700", "color": value_color, "letterSpacing": "-0.02em"}),
                    html.Span(suffix, style={"fontSize": "14px", "color": TEXT_MID, "marginLeft": "4px"})
                ],
                style={"display": "flex", "alignItems": "baseline"}
            )
        ]
    )

def nav_bar(current_path):
    is_config = current_path == "/config"
    return html.Div(
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "padding": "1.5rem 0",
            "borderBottom": f"1px solid {BORDER}",
            "marginBottom": "2rem",
            "maxWidth": "1100px",
            "margin": "0 auto 2rem auto",
        },
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "12px"},
                children=[
                    html.Div(
                        "E",
                        style={
                            "width": "36px",
                            "height": "36px",
                            "borderRadius": "8px",
                            "background": f"linear-gradient(135deg, {RED_MAIN} 0%, {RED_SEC} 100%)",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "fontSize": "18px",
                            "fontWeight": "800",
                            "color": WHITE
                        }
                    ),
                    html.Div([
                        html.Div("Etherea Labs", style={"fontSize": "15px", "fontWeight": "700", "letterSpacing": "-0.01em"}),
                        html.Div("Value Projection Dashboard", style={"fontSize": "11px", "color": TEXT_MUTE})
                    ])
                ]
            ),
            dcc.Link(
                "Configure Parameters" if not is_config else "← Back to Dashboard",
                href="/config" if not is_config else "/",
                style={
                    "background": "rgba(255, 255, 255, 0.05)" if is_config else f"linear-gradient(135deg, {RED_MAIN} 0%, {RED_SEC} 100%)",
                    "color": WHITE,
                    "border": f"1px solid {BORDER}" if is_config else "none",
                    "padding": "8px 16px",
                    "borderRadius": "8px",
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "textDecoration": "none",
                    "transition": "all 0.2s ease-in-out",
                }
            )
        ]
    )

# ── Home Layout ─────────────────────────────────────────────────────────────
def home_layout():
    return html.Div(
        style={"padding": "0 1.5rem 3rem 1.5rem", "maxWidth": "1150px", "margin": "0 auto"},
        children=[
            nav_bar("/"),
            
            # Title Section
            html.Div(
                style={"marginBottom": "2rem"},
                children=[
                    html.H1(id="main-title", style={"fontSize": "32px", "fontWeight": "800", "letterSpacing": "-0.03em", "margin": "0 0 8px 0"}),
                    html.P("See how upgrading to a professional Etherea Labs website directly boosts your sales and bottom line.", style={"color": TEXT_MID, "margin": "0", "fontSize": "14px"})
                ]
            ),

            # Main Grid Layout
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr",
                    "gap": "2rem",
                },
                id="main-responsive-grid",
                children=[
                    # Left Column: Inputs & Sliders
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "1.5rem"},
                        children=[
                            html.Div(
                                style={
                                    "background": BG_CARD,
                                    "border": f"1px solid {BORDER}",
                                    "borderRadius": "16px",
                                    "padding": "1.75rem",
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "1.75rem"
                                },
                                children=[
                                    # Current Units Sold
                                    html.Div([
                                        html.Div(
                                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline", "marginBottom": "10px"},
                                            children=[
                                                html.Span("Annual Sales Volume", style={"fontSize": "13px", "fontWeight": "600", "color": WHITE}),
                                                html.Span(id="units-slider-val", style={"fontSize": "18px", "fontWeight": "700", "color": RED_MAIN})
                                            ]
                                        ),
                                        dcc.Slider(
                                            id="units-slider",
                                            min=10, max=5000, step=10, value=150,
                                            marks=None,
                                            tooltip={"always_visible": False}
                                        )
                                    ]),

                                    # Profit per Unit
                                    html.Div([
                                        html.Div(
                                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline", "marginBottom": "10px"},
                                            children=[
                                                html.Span("Profit per Sale", style={"fontSize": "13px", "fontWeight": "600", "color": WHITE}),
                                                html.Span(id="profit-slider-val", style={"fontSize": "18px", "fontWeight": "700", "color": RED_MAIN})
                                            ]
                                        ),
                                        dcc.Slider(
                                            id="profit-slider",
                                            min=10, max=5000, step=10, value=250,
                                            marks=None,
                                            tooltip={"always_visible": False}
                                        )
                                    ]),

                                    # Conversion Lift slider
                                    html.Div([
                                        html.Div(
                                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline", "marginBottom": "10px"},
                                            children=[
                                                html.Span("Sales Lift from Premium Design", style={"fontSize": "13px", "fontWeight": "600", "color": WHITE}),
                                                html.Span(id="conversion-slider-val", style={"fontSize": "18px", "fontWeight": "700", "color": RED_MAIN})
                                            ]
                                        ),
                                        dcc.Slider(
                                            id="conversion-slider",
                                            min=5, max=100, step=5, value=25,
                                            marks=None,
                                            tooltip={"always_visible": False}
                                        )
                                    ]),

                                    # Traffic Growth slider
                                    html.Div([
                                        html.Div(
                                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline", "marginBottom": "10px"},
                                            children=[
                                                html.Span("Traffic Growth from SEO & Speed", style={"fontSize": "13px", "fontWeight": "600", "color": WHITE}),
                                                html.Span(id="traffic-slider-val", style={"fontSize": "18px", "fontWeight": "700", "color": RED_MAIN})
                                            ]
                                        ),
                                        dcc.Slider(
                                            id="traffic-slider",
                                            min=0, max=100, step=5, value=20,
                                            marks=None,
                                            tooltip={"always_visible": False}
                                        )
                                    ]),
                                ]
                            ),

                            # Tier Display Information (Recommended Website Package + Payback Period)
                            html.Div(
                                style={
                                    "background": "rgba(255, 18, 10, 0.05)",
                                    "border": f"1px dashed {BORDER}",
                                    "borderRadius": "12px",
                                    "padding": "1.25rem",
                                },
                                children=[
                                    html.Div("Recommended Website Package", style={"fontSize": "11px", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": RED_MAIN, "fontWeight": "700", "marginBottom": "8px"}),
                                    html.Div(
                                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"},
                                        children=[
                                            html.Div([
                                                html.Div("Package Name", style={"fontSize": "11px", "color": TEXT_MUTE}),
                                                html.Div(id="tier-name-val", style={"fontSize": "15px", "fontWeight": "600", "color": WHITE})
                                            ]),
                                            html.Div([
                                                html.Div("One-time Setup Cost", style={"fontSize": "11px", "color": TEXT_MUTE}),
                                                html.Div(id="tier-cost-val", style={"fontSize": "15px", "fontWeight": "600", "color": WHITE})
                                            ]),
                                        ]
                                    ),
                                    html.Div(
                                        style={"borderTop": f"1px dashed {BORDER}", "marginTop": "10px", "paddingTop": "10px"},
                                        children=[
                                            html.Div("Expected Payback Period", style={"fontSize": "11px", "color": TEXT_MUTE}),
                                            html.Div(id="metric-payback", style={"fontSize": "16px", "fontWeight": "700", "color": WHITE})
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),

                    # Right Column: Metrics Grid (Strictly 2 per row - 2x2 layout) & Chart
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "1.5rem"},
                        children=[
                            # Metric Cards Grid (strictly 2x2 columns)
                            html.Div(
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "1fr 1fr",
                                    "gap": "1rem"
                                },
                                children=[
                                    metric_card("Your Website Investment", "metric-cost", prefix="$"),
                                    metric_card("New Annual Sales Volume", "metric-units", suffix=" orders"),
                                    metric_card("Added Business Profit", "metric-net-profit", prefix="$", value_color=WHITE),
                                    metric_card("Return on Investment (ROI)", "metric-roi", suffix="%"),
                                ]
                            ),

                            # Graphic Analysis Panel
                            html.Div(
                                style={
                                    "background": BG_CARD,
                                    "border": f"1px solid {BORDER}",
                                    "borderRadius": "16px",
                                    "padding": "1.5rem",
                                },
                                children=[
                                    html.Div(
                                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1rem"},
                                        children=[
                                            html.Div([
                                                html.Div("Projected Net Profit Trajectory", style={"fontSize": "14px", "fontWeight": "700", "color": WHITE}),
                                                html.Div("Growth in business profits minus the initial setup cost", style={"fontSize": "11px", "color": TEXT_MUTE})
                                            ]),
                                            html.Span(id="timeline-badge", style={"fontSize": "11px", "background": "rgba(255, 255, 255, 0.08)", "padding": "4px 8px", "borderRadius": "4px", "color": TEXT_MID, "fontWeight": "600"})
                                        ]
                                    ),
                                    dcc.Graph(
                                        id="cumulative-chart",
                                        config={"displayModeBar": False},
                                        style={"height": "280px"}
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# ── Config Layout ───────────────────────────────────────────────────────────
def config_layout():
    return html.Div(
        style={"padding": "0 1.5rem 3rem 1.5rem", "maxWidth": "800px", "margin": "0 auto"},
        children=[
            nav_bar("/config"),
            
            html.Div(
                style={"marginBottom": "2rem"},
                children=[
                    html.H1("ROI Configuration Panel", style={"fontSize": "30px", "fontWeight": "800", "letterSpacing": "-0.03em", "margin": "0 0 8px 0"}),
                    html.P("Customize the underlying parameters of the calculator. Click 'Save Configuration' to apply changes.", style={"color": TEXT_MID, "margin": "0", "fontSize": "14px"})
                ]
            ),

            html.Div(
                style={
                    "background": BG_CARD,
                    "border": f"1px solid {BORDER}",
                    "borderRadius": "16px",
                    "padding": "2rem",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "1.75rem",
                    "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.2)"
                },
                children=[
                    # Global Settings
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1.5rem"},
                        children=[
                            html.Div([
                                html.Label("Product/Service Name", style={"fontSize": "12px", "fontWeight": "600", "color": WHITE, "display": "block", "marginBottom": "6px"}),
                                dcc.Input(id="cfg-product-name", type="text", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                            ]),
                            html.Div([
                                html.Label("Analysis Timeline (Months)", style={"fontSize": "12px", "fontWeight": "600", "color": WHITE, "display": "block", "marginBottom": "6px"}),
                                dcc.Input(id="cfg-timeline", type="number", min=1, max=120, style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                            ]),
                        ]
                    ),

                    html.Hr(style={"border": "none", "borderTop": f"1px solid {BORDER}", "margin": "1rem 0"}),

                    # Tier Settings Header
                    html.Div([
                        html.Div("Investment Tiers", style={"fontSize": "15px", "fontWeight": "700", "color": WHITE, "marginBottom": "4px"}),
                        html.Div("Define the cost structure. Tiers switch dynamically based on client's Current Sales Volume limit.", style={"fontSize": "12px", "color": TEXT_MUTE})
                    ]),

                    # Tiers config table
                    html.Div(
                        children=[
                            # Tier 1
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1.2fr", "gap": "1.25rem", "alignItems": "end", "marginBottom": "1rem"},
                                children=[
                                    html.Div([
                                        html.Label("Tier 1 Name", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t1-name", type="text", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                    html.Div([
                                        html.Label("Fixed Cost ($)", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t1-cost", type="number", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                    html.Div([
                                        html.Label("Sales Volume Limit (Up to)", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t1-limit", type="number", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                ]
                            ),
                            # Tier 2
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1.2fr", "gap": "1.25rem", "alignItems": "end", "marginBottom": "1rem"},
                                children=[
                                    html.Div([
                                        html.Label("Tier 2 Name", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t2-name", type="text", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                    html.Div([
                                        html.Label("Fixed Cost ($)", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t2-cost", type="number", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                    html.Div([
                                        html.Label("Sales Volume Limit (Up to)", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t2-limit", type="number", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                ]
                            ),
                            # Tier 3 (Infinite/Catch-All Limit)
                            html.Div(
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1.2fr", "gap": "1.25rem", "alignItems": "end"},
                                children=[
                                    html.Div([
                                        html.Label("Tier 3 Name", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t3-name", type="text", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                    html.Div([
                                        html.Label("Fixed Cost ($)", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(id="cfg-t3-cost", type="number", style={"background": BG_DEEP, "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": WHITE, "padding": "10px", "width": "100%", "boxSizing": "border-box"})
                                    ]),
                                    html.Div([
                                        html.Label("Sales Volume Limit", style={"fontSize": "11px", "color": TEXT_MUTE, "display": "block", "marginBottom": "6px"}),
                                        dcc.Input(value="Unlimited", disabled=True, style={"background": "rgba(255, 255, 255, 0.05)", "border": f"1px solid {BORDER}", "borderRadius": "8px", "color": TEXT_MUTE, "padding": "10px", "width": "100%", "boxSizing": "border-box", "cursor": "not-allowed"})
                                    ]),
                                ]
                            ),
                        ]
                    ),

                    # Action buttons
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between", "marginTop": "1.5rem"},
                        children=[
                            html.Button(
                                "Reset to Defaults",
                                id="btn-reset",
                                n_clicks=0,
                                style={"background": "transparent", "border": f"1px solid {RED_MAIN}", "color": RED_MAIN, "padding": "10px 20px", "borderRadius": "8px", "fontSize": "13px", "fontWeight": "600", "cursor": "pointer"}
                            ),
                            html.Button(
                                "Save Configuration",
                                id="btn-save",
                                n_clicks=0,
                                style={"background": f"linear-gradient(135deg, {RED_MAIN} 0%, {RED_SEC} 100%)", "border": "none", "color": WHITE, "padding": "10px 24px", "borderRadius": "8px", "fontSize": "13px", "fontWeight": "600", "cursor": "pointer"}
                            )
                        ]
                    ),
                    
                    html.Div(id="cfg-status-message", style={"fontSize": "13px", "textAlign": "right", "fontWeight": "500"})
                ]
            )
        ]
    )

# ── Dynamic Route Handling Callback ─────────────────────────────────────────
@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_route(pathname):
    if pathname == "/config":
        return config_layout()
    return home_layout()

# ── Configuration Save & Load Callbacks ──────────────────────────────────────
@callback(
    Output("config-store", "data"),
    Output("cfg-status-message", "children"),
    Output("cfg-status-message", "style"),
    Input("btn-save", "n_clicks"),
    Input("btn-reset", "n_clicks"),
    State("cfg-product-name", "value"),
    State("cfg-timeline", "value"),
    State("cfg-t1-name", "value"),
    State("cfg-t1-cost", "value"),
    State("cfg-t1-limit", "value"),
    State("cfg-t2-name", "value"),
    State("cfg-t2-cost", "value"),
    State("cfg-t2-limit", "value"),
    State("cfg-t3-name", "value"),
    State("cfg-t3-cost", "value"),
    State("config-store", "data")
)
def manage_config(save_clicks, reset_clicks, name, timeline, t1_name, t1_cost, t1_limit, t2_name, t2_cost, t2_limit, t3_name, t3_cost, current_store):
    triggered = ctx.triggered_id
    
    if triggered == "btn-reset":
        return DEFAULT_CONFIG, "Configuration reset to defaults.", {"color": RED_MAIN}
        
    if triggered == "btn-save":
        # Validate inputs
        if not name or timeline is None:
            return current_store, "Please provide product name and timeline.", {"color": RED_MAIN}
        
        updated_config = {
            "product_name": name,
            "timeline_months": int(timeline),
            "tiers": [
                {"name": t1_name or "Starter Package", "cost": float(t1_cost or 0), "limit": int(t1_limit or 100)},
                {"name": t2_name or "Growth Package", "cost": float(t2_cost or 0), "limit": int(t2_limit or 500)},
                {"name": t3_name or "Enterprise Package", "cost": float(t3_cost or 0), "limit": 999999}
            ]
        }
        return updated_config, "Configuration saved successfully!", {"color": WHITE}

    # Initial load of config values
    return current_store or DEFAULT_CONFIG, "", {}

# Populate config inputs when config page is loaded
@callback(
    Output("cfg-product-name", "value"),
    Output("cfg-timeline", "value"),
    Output("cfg-t1-name", "value"),
    Output("cfg-t1-cost", "value"),
    Output("cfg-t1-limit", "value"),
    Output("cfg-t2-name", "value"),
    Output("cfg-t2-cost", "value"),
    Output("cfg-t2-limit", "value"),
    Output("cfg-t3-name", "value"),
    Output("cfg-t3-cost", "value"),
    Input("url", "pathname"),
    State("config-store", "data")
)
def populate_config_inputs(pathname, store_data):
    if pathname != "/config":
        return [dash.no_update] * 10
        
    cfg = store_data or DEFAULT_CONFIG
    t = cfg["tiers"]
    return (
        cfg["product_name"],
        cfg["timeline_months"],
        t[0]["name"], t[0]["cost"], t[0]["limit"],
        t[1]["name"], t[1]["cost"], t[1]["limit"],
        t[2]["name"], t[2]["cost"]
    )

# ── Calculator Engine Callbacks ─────────────────────────────────────────────
@callback(
    Output("main-title", "children"),
    Output("units-slider-val", "children"),
    Output("profit-slider-val", "children"),
    Output("conversion-slider-val", "children"),
    Output("traffic-slider-val", "children"),
    Output("tier-name-val", "children"),
    Output("tier-cost-val", "children"),
    Output("metric-cost", "children"),
    Output("metric-units", "children"),
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
def update_calculator(units_val, profit_val, conversion_val, traffic_val, config_data, pathname):
    if pathname == "/config":
        return [dash.no_update] * 14
        
    cfg = config_data or DEFAULT_CONFIG
    product_name = cfg["product_name"]
    timeline = cfg["timeline_months"]
    tiers = cfg["tiers"]
    
    # 1. Determine recommended plan based on current scale (units_val)
    active_tier = tiers[0]
    for tier in tiers:
        if units_val <= tier["limit"]:
            active_tier = tier
            break
            
    tier_name = active_tier["name"]
    tier_cost = active_tier["cost"]
    
    # 2. Value-selling Calculations
    # Calculate performance improvements due to Etherea Website
    conversion_multiplier = 1 + (conversion_val / 100)
    traffic_multiplier = 1 + (traffic_val / 100)
    
    new_units_val = round(units_val * conversion_multiplier * traffic_multiplier)
    additional_units = new_units_val - units_val
    
    incremental_annual_profit = additional_units * profit_val
    incremental_timeline_profit = incremental_annual_profit * (timeline / 12)
    
    net_benefit = incremental_timeline_profit - tier_cost
    roi = (net_benefit / tier_cost * 100) if tier_cost > 0 else 0
    
    # Payback period calculation
    payback_mo = (tier_cost / (incremental_annual_profit / 12)) if incremental_annual_profit > 0 else float("inf")
    
    if payback_mo == float("inf"):
        payback_str = "Never"
    elif payback_mo == 0:
        payback_str = "Immediate"
    elif payback_mo < 1:
        payback_str = "Under 1 month"
    else:
        payback_str = f"{payback_mo:.1f} months"

    # Display formatting
    def fmt_usd(v):
        return f"{round(v):,}"
        
    # 3. Chart: Cumulative Net Cash Flow trajectory of the upgrade
    months = list(range(timeline + 1))
    cash_flow = [-tier_cost + ((incremental_annual_profit / 12) * m) for m in months]
    
    fig = go.Figure()
    
    # Gradient red line & fill matching the upgrade return trajectory
    fig.add_trace(go.Scatter(
        x=months,
        y=cash_flow,
        mode="lines+markers",
        line=dict(color=RED_MAIN, width=3),
        marker=dict(size=6, color=RED_MAIN),
        name="Cumulative Return",
        fill="tozeroy",
        fillcolor="rgba(255, 18, 10, 0.1)",
        hoverinfo="x+y",
        hovertemplate="Month %{x}: $%{y:,.0f}"
    ))
    
    # Breakeven guide line
    fig.add_shape(
        type="line",
        x0=0, y0=0, x1=timeline, y1=0,
        line=dict(color="rgba(255, 255, 255, 0.2)", width=1, dash="dash")
    )
    
    # Chart Styling
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Inter, sans-serif", color=TEXT_MUTE),
        xaxis=dict(
            showgrid=False,
            tickmode="linear",
            dtick=max(1, timeline // 6),
            tickfont=dict(color=TEXT_MUTE, size=11),
            title=dict(text="Timeline (Months)", font=dict(size=10, color=TEXT_MUTE))
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            tickfont=dict(color=TEXT_MUTE, size=11),
            tickprefix="$",
            tickformat=",",
            zeroline=False
        ),
        showlegend=False,
        hovermode="x unified"
    )

    return (
        f"{product_name} ROI Projector",
        f"{units_val:,} sales/yr",
        f"${profit_val:,}",
        f"+{conversion_val}%",
        f"+{traffic_val}%",
        tier_name,
        f"${fmt_usd(tier_cost)}",
        fmt_usd(tier_cost),
        f"{new_units_val:,}",
        fmt_usd(net_benefit),
        f"{round(roi):,}",
        payback_str,
        f"{timeline}m Timeline",
        fig
    )

# ── Inject styles and meta tags ──────────────────────────────────────────────
app.index_string = f"""<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            body {{
                background-color: {BG_DEEP};
            }}
            /* Custom Range Slider Overrides in Etherea Red */
            .rc-slider-rail {{
                background-color: {BORDER} !important;
                height: 6px !important;
            }}
            .rc-slider-track {{
                background: linear-gradient(90deg, {RED_MAIN} 0%, {RED_SEC} 100%) !important;
                height: 6px !important;
            }}
            .rc-slider-handle {{
                border: 2px solid {RED_MAIN} !important;
                background-color: {BG_DEEP} !important;
                width: 18px !important;
                height: 18px !important;
                margin-top: -6px !important;
                opacity: 1 !important;
                box-shadow: none !important;
            }}
            .rc-slider-handle:hover, .rc-slider-handle:active {{
                background-color: {RED_MAIN} !important;
                box-shadow: 0 0 10px rgba(255, 18, 10, 0.4) !important;
            }}
            /* Responsive Grid */
            @media (min-width: 768px) {{
                #main-responsive-grid {{
                    grid-template-columns: minmax(320px, 1fr) minmax(400px, 1.5fr) !important;
                }}
            }}
            /* Smooth transitions */
            a, button, input {{
                transition: all 0.2s ease-in-out;
            }}
            button:hover {{
                filter: brightness(1.1);
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>"""

if __name__ == "__main__":
    app.run(debug=True, port=4006)