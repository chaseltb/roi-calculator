import math
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

# ── Brand colors ─────────────────────────────────────────────────────────────
BG_MAIN    = "#1e0704"
BG_CARD    = "#2a0905"
BG_PAGE    = "#140303"
BORDER     = "#550a04"
BORDER_DIM = "#370e08"
RED        = "#ff120a"
RED_SEC    = "#960502"
GREEN      = "#4ade80"
AMBER      = "#fbbf24"
TEXT_PRI   = "#f0e8e8"
TEXT_MUT   = "#8a6060"
GREY       = "#36454f"

# ── Helpers ───────────────────────────────────────────────────────────────────
PMIN, PMAX = 10, 5000

def slider_to_profit(t):
    """Exponential (log) scale: slider 0-100 -> $10-$5000"""
    return round(PMIN * math.pow(PMAX / PMIN, t / 100))

def fmt_usd(n):
    return "$" + f"{round(n):,}"

# ── Style helpers ─────────────────────────────────────────────────────────────
def card_style(extra=None):
    s = {
        "background": BG_CARD,
        "border": "1px solid " + BORDER,
        "borderRadius": "10px",
        "padding": "1rem",
    }
    if extra:
        s.update(extra)
    return s

def label_style():
    return {
        "fontSize": "11px",
        "letterSpacing": "0.06em",
        "textTransform": "uppercase",
        "color": TEXT_MUT,
        "marginBottom": "8px",
        "fontFamily": "Inter, sans-serif",
    }

def value_style(color=None):
    return {
        "fontFamily": "'DM Mono', monospace",
        "fontSize": "20px",
        "fontWeight": "700",
        "color": color if color else TEXT_PRI,
        "lineHeight": "1.2",
        "margin": "0",
    }

def slider_label_style():
    return {
        "fontSize": "12px",
        "letterSpacing": "0.07em",
        "textTransform": "uppercase",
        "color": TEXT_MUT,
        "fontWeight": "500",
        "fontFamily": "Inter, sans-serif",
    }

def mono_display_style():
    return {
        "fontFamily": "'DM Mono', monospace",
        "fontSize": "18px",
        "fontWeight": "500",
        "color": "#fff",
    }

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        (
            "https://fonts.googleapis.com/css2?"
            "family=DM+Mono:wght@400;500"
            "&family=Inter:wght@400;500;600"
            "&display=swap"
        ),
    ],
    title="ROI Calculator - Etherea Labs",
)

# Inject slider + global CSS via index_string
_css = (
    "body{background:" + BG_PAGE + ";}"
    ".etherea-slider .rc-slider-rail{background:" + BORDER + "!important;height:3px!important}"
    ".etherea-slider .rc-slider-track{background:" + RED_SEC + "!important;height:3px!important}"
    ".etherea-slider .rc-slider-handle{"
        "background:" + RED + "!important;"
        "border:3px solid " + BG_MAIN + "!important;"
        "box-shadow:0 0 0 1px " + RED_SEC + "!important;"
        "width:18px!important;height:18px!important;"
        "margin-top:-8px!important;opacity:1!important}"
    ".etherea-slider .rc-slider-handle:hover,"
    ".etherea-slider .rc-slider-handle:active{"
        "box-shadow:0 0 0 2px " + RED + "!important}"
    ".settings-toggle{"
        "background:none;border:none;padding:0;"
        "font-family:Inter,sans-serif;"
        "font-size:11px;letter-spacing:0.1em;"
        "text-transform:uppercase;color:#a0b4bf;"
        "cursor:pointer;display:flex;align-items:center;gap:8px;width:100%}"
    ".settings-toggle:hover{color:#f0e8e8}"
    ".toggle-arrow{transition:transform 0.2s ease;display:inline-block;font-size:10px}"
    ".toggle-arrow.open{transform:rotate(90deg)}"
)

app.index_string = (
    "<!DOCTYPE html><html><head>"
    "{%metas%}<title>{%title%}</title>{%favicon%}{%css%}"
    "<style>" + _css + "</style>"
    "</head><body>"
    "{%app_entry%}{%config%}{%scripts%}{%renderer%}"
    "</body></html>"
)

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={"background": BG_PAGE, "minHeight": "100vh", "padding": "2rem 10rem"},
    children=[

        # ── Collapsible config panel ──────────────────────────────────────────
        dbc.Container(
            style={"marginBottom": "1.5rem"},
            children=[
                html.Div(
                    style={
                        "background": GREY,
                        "border": "1px solid #4a5a66",
                        "borderRadius": "12px",
                        "overflow": "hidden",
                    },
                    children=[
                        # Toggle button header
                        html.Button(
                            children=[
                                html.Span(id="toggle-arrow", className="toggle-arrow", children="▶"),
                                "  Calculator settings",
                            ],
                            id="settings-toggle",
                            className="settings-toggle",
                            n_clicks=0,
                            style={"padding": "1rem 1.25rem"},
                        ),
                        # Collapsible body
                        dbc.Collapse(
                            id="settings-collapse",
                            is_open=False,
                            children=html.Div(
                                style={
                                    "padding": "0 1.25rem 1.25rem 1.25rem",
                                    "borderTop": "1px solid #4a5a66",
                                    "paddingTop": "1rem",
                                },
                                children=[
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label(
                                                "Unit label",
                                                style=slider_label_style(),
                                            ),
                                            dcc.Input(
                                                id="unit-label",
                                                type="text",
                                                value="units",
                                                placeholder="e.g. roofs, services, customers",
                                                debounce=True,
                                                style={
                                                    "background": "#29363e",
                                                    "border": "1px solid #4a5a66",
                                                    "borderRadius": "8px",
                                                    "color": TEXT_PRI,
                                                    "padding": "8px 12px",
                                                    "fontSize": "14px",
                                                    "fontFamily": "Inter, sans-serif",
                                                    "width": "100%",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ], md=6),
                                        dbc.Col([
                                            html.Label(
                                                "Max units sold per year",
                                                style=slider_label_style(),
                                            ),
                                            dcc.Input(
                                                id="max-units",
                                                type="number",
                                                value=1000,
                                                min=10,
                                                max=100000,
                                                step=10,
                                                debounce=True,
                                                style={
                                                    "background": "#29363e",
                                                    "border": "1px solid #4a5a66",
                                                    "borderRadius": "8px",
                                                    "color": TEXT_PRI,
                                                    "padding": "8px 12px",
                                                    "fontSize": "14px",
                                                    "fontFamily": "Inter, sans-serif",
                                                    "width": "100%",
                                                    "marginTop": "6px",
                                                },
                                            ),
                                        ], md=6),
                                    ]),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),

        # ── Main ROI container ────────────────────────────────────────────────
        dbc.Container(
            style={
                "background": BG_MAIN,
                "border": "1px solid " + BORDER,
                "borderRadius": "16px",
                "padding": "2rem",
            },
            children=[

                # Badge
                html.Div(
                    "ROI Calculator",
                    style={
                        "display": "inline-block",
                        "fontSize": "11px",
                        "letterSpacing": "0.1em",
                        "textTransform": "uppercase",
                        "padding": "4px 12px",
                        "borderRadius": "20px",
                        "background": "rgba(255,18,10,0.15)",
                        "color": RED,
                        "border": "1px solid rgba(255,18,10,0.3)",
                        "marginBottom": "14px",
                        "fontFamily": "'DM Mono', monospace",
                    },
                ),

                html.H1(
                    "Website Investment ROI",
                    style={
                        "fontSize": "22px",
                        "fontWeight": "600",
                        "color": "#fff",
                        "marginBottom": "4px",
                        "fontFamily": "Inter, sans-serif",
                    },
                ),

                html.P(
                    "Estimate your return from a new website by Etherea Labs",
                    style={
                        "fontSize": "13px",
                        "color": TEXT_MUT,
                        "marginBottom": "2rem",
                        "fontFamily": "Inter, sans-serif",
                    },
                ),

                # Investment cost slider
                dbc.Row([
                    dbc.Col(
                        html.Label("Investment cost", style=slider_label_style()),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Span(id="inv-display", style=mono_display_style()),
                        className="text-end",
                    ),
                ], className="mb-2 align-items-baseline"),
                dcc.Slider(
                    id="inv-slider",
                    min=500, max=20000, step=100, value=1500,
                    marks=None,
                    tooltip={"always_visible": False},
                    className="etherea-slider",
                ),
                html.Div(style={"marginBottom": "1.5rem"}),

                # Units sold per year slider
                dbc.Row([
                    dbc.Col(
                        html.Label(id="units-label", children="Units sold per year",
                                   style=slider_label_style()),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Span(id="units-display", style=mono_display_style()),
                        className="text-end",
                    ),
                ], className="mb-2 align-items-baseline"),
                dcc.Slider(
                    id="units-slider",
                    min=1, max=1000, step=1, value=100,
                    marks=None,
                    tooltip={"always_visible": False},
                    className="etherea-slider",
                ),
                html.Div(style={"marginBottom": "1.5rem"}),

                # Profit per unit slider (log scale, internal 0-100)
                dbc.Row([
                    dbc.Col(
                        html.Label(id="profit-label", children="Profit per unit",
                                   style=slider_label_style()),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Span(id="profit-display", style=mono_display_style()),
                        className="text-end",
                    ),
                ], className="mb-2 align-items-baseline"),
                dcc.Slider(
                    id="profit-slider",
                    min=0, max=100, step=0.5, value=37.1,
                    marks=None,
                    tooltip={"always_visible": False},
                    className="etherea-slider",
                ),

                html.Hr(style={"borderTop": "1px solid " + BORDER_DIM, "margin": "1.5rem 0"}),

                # Result cards row 1: revenue + net profit
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.P("Annual revenue", style=label_style()),
                            html.P(id="ann-rev", style=value_style()),
                        ], style=card_style()),
                        md=6,
                    ),
                    dbc.Col(
                        html.Div([
                            html.P("Annual net profit", style=label_style()),
                            html.P(id="ann-profit", style=value_style(GREEN)),
                        ], style=card_style()),
                        md=6,
                    ),
                ], className="mb-2 g-2"),

                # Result cards row 2: ROI + breakeven + payback
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.P("ROI (12-month)", style=label_style()),
                            html.P(id="roi-pct", style=value_style(GREEN)),
                        ], style=card_style()),
                        md=4,
                    ),
                    dbc.Col(
                        html.Div([
                            html.P(id="breakeven-label", children="Breakeven point",
                                   style=label_style()),
                            html.P(id="breakeven", style=value_style(AMBER)),
                        ], style=card_style()),
                        md=4,
                    ),
                    dbc.Col(
                        html.Div([
                            html.P("Payback period", style=label_style()),
                            html.P(id="payback-card", style=value_style()),
                        ], style=card_style()),
                        md=4,
                    ),
                ], className="mb-3 g-2"),

                # Breakdown table
                html.Div(
                    style=card_style({"padding": "1rem 1.25rem"}),
                    children=[
                        html.Div([
                            html.Span(
                                "Annual revenue (units x profit)",
                                style={"color": TEXT_MUT, "fontSize": "13px",
                                       "fontFamily": "Inter, sans-serif"},
                            ),
                            html.Span(
                                id="b-ann-rev",
                                style={"fontFamily": "'DM Mono', monospace",
                                       "color": TEXT_PRI, "fontSize": "13px"},
                            ),
                        ], style={"display": "flex", "justifyContent": "space-between",
                                  "padding": "6px 0",
                                  "borderBottom": "1px solid " + BORDER_DIM}),
                        html.Div([
                            html.Span(
                                "Investment cost",
                                style={"color": TEXT_MUT, "fontSize": "13px",
                                       "fontFamily": "Inter, sans-serif"},
                            ),
                            html.Span(
                                id="b-inv",
                                style={"fontFamily": "'DM Mono', monospace",
                                       "color": TEXT_PRI, "fontSize": "13px"},
                            ),
                        ], style={"display": "flex", "justifyContent": "space-between",
                                  "padding": "6px 0",
                                  "borderBottom": "1px solid " + BORDER_DIM}),
                        html.Div([
                            html.Span(
                                id="b-breakeven-label",
                                children="Units to break even",
                                style={"color": TEXT_MUT, "fontSize": "13px",
                                       "fontFamily": "Inter, sans-serif"},
                            ),
                            html.Span(
                                id="b-breakeven",
                                style={"fontFamily": "'DM Mono', monospace",
                                       "color": TEXT_PRI, "fontSize": "13px"},
                            ),
                        ], style={"display": "flex", "justifyContent": "space-between",
                                  "padding": "6px 0",
                                  "borderBottom": "1px solid " + BORDER_DIM}),
                        html.Div([
                            html.Span(
                                "12-month net gain",
                                style={"color": TEXT_MUT, "fontSize": "14px",
                                       "fontWeight": "600",
                                       "fontFamily": "Inter, sans-serif"},
                            ),
                            html.Span(
                                id="b-net",
                                style={"fontFamily": "'DM Mono', monospace",
                                       "color": TEXT_PRI, "fontSize": "14px",
                                       "fontWeight": "600"},
                            ),
                        ], style={"display": "flex", "justifyContent": "space-between",
                                  "padding": "6px 0"}),
                    ],
                ),

                # CTA
                html.Div(
                    style={
                        "marginTop": "1.5rem",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "flexWrap": "wrap",
                        "gap": "1rem",
                    },
                    children=[
                        html.P(
                            "Ready to turn this into reality? Etherea Labs builds "
                            "high-performance websites for Raleigh businesses that convert.",
                            style={
                                "fontSize": "12px",
                                "color": TEXT_MUT,
                                "lineHeight": "1.6",
                                "maxWidth": "340px",
                                "margin": "0",
                                "fontFamily": "Inter, sans-serif",
                            },
                        ),
                        html.A(
                            "Start your project ->",
                            href="https://etherealabs.co/contact",
                            target="_blank",
                            style={
                                "display": "inline-block",
                                "fontSize": "13px",
                                "fontWeight": "600",
                                "padding": "10px 20px",
                                "borderRadius": "8px",
                                "background": RED,
                                "color": "#fff",
                                "textDecoration": "none",
                                "fontFamily": "Inter, sans-serif",
                                "letterSpacing": "0.02em",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(
    Output("settings-collapse", "is_open"),
    Output("toggle-arrow", "className"),
    Input("settings-toggle", "n_clicks"),
    State("settings-collapse", "is_open"),
)
def toggle_settings(n_clicks, is_open):
    if n_clicks:
        new_open = not is_open
        arrow_class = "toggle-arrow open" if new_open else "toggle-arrow"
        return new_open, arrow_class
    return is_open, "toggle-arrow"


@callback(
    Output("units-slider", "max"),
    Input("max-units", "value"),
)
def update_max_units(max_val):
    return max_val if max_val else 1000


@callback(
    Output("units-label",       "children"),
    Output("profit-label",      "children"),
    Output("breakeven-label",   "children"),
    Output("b-breakeven-label", "children"),
    Input("unit-label", "value"),
)
def update_labels(unit):
    u = (unit or "units").strip()
    singular = u.rstrip("s") if u.endswith("s") and len(u) > 1 else u
    return (
        u.capitalize() + " sold per year",
        "Profit per " + singular,
        "Breakeven point (" + u + ")",
        u.capitalize() + " to break even",
    )


@callback(
    Output("inv-display",    "children"),
    Output("units-display",  "children"),
    Output("profit-display", "children"),
    Output("ann-rev",        "children"),
    Output("ann-profit",     "children"),
    Output("roi-pct",        "children"),
    Output("breakeven",      "children"),
    Output("payback-card",   "children"),
    Output("b-ann-rev",      "children"),
    Output("b-inv",          "children"),
    Output("b-breakeven",    "children"),
    Output("b-net",          "children"),
    Input("inv-slider",      "value"),
    Input("units-slider",    "value"),
    Input("profit-slider",   "value"),
    Input("unit-label",      "value"),
)
def update_results(inv, units, profit_t, unit_label):
    u             = (unit_label or "units").strip()
    inv           = inv if inv else 1500
    units         = units if units else 100
    profit        = slider_to_profit(profit_t if profit_t is not None else 37.1)
    ann_rev       = units * profit
    net_gain      = ann_rev - inv
    roi           = (net_gain / inv) * 100
    payback_mo    = inv / (ann_rev / 12) if ann_rev > 0 else float("inf")
    breakeven_qty = math.ceil(inv / profit) if profit > 0 else 0

    if payback_mo < 1:
        payback_str = "< 1 month"
    elif payback_mo < 12:
        payback_str = f"{payback_mo:.1f} mo"
    else:
        payback_str = f"{payback_mo / 12:.1f} yrs"

    return (
        fmt_usd(inv),
        f"{units:,} {u}",
        fmt_usd(profit),
        fmt_usd(ann_rev),
        fmt_usd(net_gain),
        f"{round(roi)}%",
        f"{breakeven_qty:,} {u}",
        payback_str,
        fmt_usd(ann_rev),
        "-" + fmt_usd(inv),
        f"{breakeven_qty:,} {u} @ {fmt_usd(profit)} each",
        fmt_usd(net_gain),
    )


if __name__ == "__main__":
    app.run(debug=True)