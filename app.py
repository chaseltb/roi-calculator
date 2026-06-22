import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import plotly.graph_objects as go

# ── Brand colors ──────────────────────────────────────────────────────────────
BG_MAIN   = "#370e08"
BG_CARD   = "#550a04"
BG_DEEP   = "#1a0503"
RED_MAIN  = "#ff120a"
RED_SEC   = "#960502"
WHITE     = "#ffffff"
TEXT_MID  = "#c07070"
TEXT_MUTE = "#a07070"
BORDER    = "#6e1208"

app = dash.Dash(
    __name__,
    title="ROI Calculator — Etherea Labs",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# ── Shared styles ─────────────────────────────────────────────────────────────
card_style = {
    "background": BG_CARD,
    "border": f"1px solid {BORDER}",
    "borderRadius": "12px",
    "padding": "1.25rem 1.5rem",
}

label_style = {
    "fontSize": "11px",
    "letterSpacing": "0.08em",
    "textTransform": "uppercase",
    "color": TEXT_MUTE,
    "marginBottom": "4px",
    "fontWeight": "500",
}

value_style = {
    "fontSize": "26px",
    "fontWeight": "600",
    "color": WHITE,
    "fontVariantNumeric": "tabular-nums",
    "lineHeight": "1.2",
}

slider_label_style = {
    "fontSize": "12px",
    "letterSpacing": "0.07em",
    "textTransform": "uppercase",
    "color": TEXT_MID,
    "fontWeight": "500",
}

slider_value_style = {
    "fontSize": "20px",
    "fontWeight": "600",
    "color": WHITE,
    "fontVariantNumeric": "tabular-nums",
}

input_style = {
    "background": BG_MAIN,
    "border": f"1px solid {BORDER}",
    "borderRadius": "8px",
    "color": WHITE,
    "fontSize": "14px",
    "padding": "8px 12px",
    "outline": "none",
    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
    "width": "100%",
    "boxSizing": "border-box",
}

number_input_style = {
    **input_style,
    "width": "110px",
    "fontVariantNumeric": "tabular-nums",
}


def metric_card(card_id, label, accent_color=WHITE):
    return html.Div(
        [
            html.Div(label, style=label_style),
            html.Div("—", id=card_id, style={**value_style, "color": accent_color}),
        ],
        style=card_style,
    )


def breakdown_row(label, value_id):
    return html.Div(
        [
            html.Span(label, style={"color": TEXT_MUTE, "fontSize": "13px"}),
            html.Span("—", id=value_id, style={
                "fontSize": "13px",
                "color": "#f0e8e8",
                "fontVariantNumeric": "tabular-nums",
            }),
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "padding": "8px 0",
            "borderBottom": f"1px solid {BORDER}",
        },
    )


# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={
        "background": BG_DEEP,
        "minHeight": "100vh",
        "padding": "1rem",
        "margin": "0",
        "fontFamily": "'Inter', 'Segoe UI', sans-serif",
        "color": WHITE,
    },
    children=[

        # ── Header ────────────────────────────────────────────────────────────
        html.Div(
            style={"maxWidth": "960px", "margin": "0 auto 2rem"},
            children=[
                # Logo row
                html.Div(
                    style={
                        "display": "flex", "alignItems": "center",
                        "gap": "10px", "marginBottom": "20px",
                    },
                    children=[
                        html.Div(
                            "E",
                            style={
                                "width": "32px", "height": "32px", "borderRadius": "8px",
                                "background": RED_MAIN,
                                "display": "flex", "alignItems": "center",
                                "justifyContent": "center",
                                "fontSize": "16px", "fontWeight": "700", "color": WHITE,
                                "flexShrink": "0",
                            },
                        ),
                        html.Span("Etherea Labs", style={
                            "fontSize": "16px", "fontWeight": "700", "color": WHITE,
                            "letterSpacing": "-0.01em",
                        }),
                        html.Span("·", style={"color": BORDER, "fontSize": "18px", "margin": "0 2px"}),
                        html.Span("Premium Web Design & Development", style={
                            "fontSize": "13px", "color": TEXT_MUTE,
                        }),
                    ],
                ),
                html.Div(
                    "● ROI Calculator",
                    style={
                        "display": "inline-block",
                        "fontSize": "11px", "letterSpacing": "0.1em",
                        "textTransform": "uppercase",
                        "background": "rgba(255,18,10,0.15)", "color": RED_MAIN,
                        "border": "1px solid rgba(255,18,10,0.3)",
                        "borderRadius": "20px", "padding": "4px 12px",
                        "marginBottom": "10px",
                    },
                ),
                html.H1("Website Investment ROI", style={
                    "fontSize": "32px", "fontWeight": "700",
                    "margin": "0 0 6px", "color": WHITE,
                    "letterSpacing": "-0.02em",
                }),
                html.P(
                    "Estimate your return from a new Etherea Labs website. Adjust the inputs below to match your business.",
                    style={"fontSize": "14px", "color": TEXT_MUTE, "margin": "0"},
                ),
            ],
        ),

        # ── Config bar: service tier + editable prices + product name ─────────
        html.Div(
            style={
                "maxWidth": "960px", "margin": "0 auto 1.5rem",
                # **card_style,
                "display": "grid",
                "gridTemplateColumns": "auto auto auto 1fr",
                "gap": "1.5rem",
                "alignItems": "end",
            },
            children=[
                # Service tier dropdown
                html.Div([
                    html.Div("Service Tier", style={**label_style, "marginBottom": "6px"}),
                    dcc.Dropdown(
                        id="tier-dropdown",
                        options=[
                            {"label": "Starter",  "value": "starter"},
                            {"label": "Growth",   "value": "growth"},
                            {"label": "Custom",   "value": "custom"},
                        ],
                        value="starter",
                        clearable=False,
                        style={"width": "160px", "fontFamily": "'Inter','Segoe UI',sans-serif"},
                    ),
                ]),

                # Starter price
                html.Div([
                    html.Div("Starter Price ($)", style={**label_style, "marginBottom": "6px"}),
                    dcc.Input(
                        id="starter-price",
                        type="number", value=809, min=1,
                        style=number_input_style,
                        debounce=True,
                    ),
                ]),

                # Growth price
                html.Div([
                    html.Div("Growth Price ($)", style={**label_style, "marginBottom": "6px"}),
                    dcc.Input(
                        id="growth-price",
                        type="number", value=1237, min=1,
                        style=number_input_style,
                        debounce=True,
                    ),
                ]),

                # Product / service name
                html.Div([
                    html.Div("Product / Service Name", style={**label_style, "marginBottom": "6px"}),
                    dcc.Input(
                        id="product-name",
                        type="text",
                        value="Website Package",
                        placeholder="e.g. Landing Page, SEO Audit…",
                        style=input_style,
                        debounce=False,
                    ),
                ]),
            ],
        ),

        # ── Main grid ─────────────────────────────────────────────────────────
        html.Div(
            style={
                "maxWidth": "960px", "margin": "0 auto 1.5rem",
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "1.5rem",
            },
            children=[

                # Left: sliders + breakdown
                html.Div(
                    style={**card_style, "display": "flex", "flexDirection": "column", "gap": "1.5rem"},
                    children=[
                        # Investment cost
                        html.Div([
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "marginBottom": "8px"},
                                children=[
                                    html.Span("Investment Cost", style=slider_label_style),
                                    html.Span("$809", id="inv-display", style=slider_value_style),
                                ],
                            ),
                            dcc.Slider(
                                id="inv-slider",
                                min=100, max=20000, step=50, value=809,
                                marks=None,
                                tooltip={"always_visible": False},
                            ),
                        ]),

                        # Units per year — label updates with product name
                        html.Div([
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "marginBottom": "8px"},
                                children=[
                                    html.Span("Units Sold per Year", id="units-label", style=slider_label_style),
                                    html.Span("144", id="units-display", style=slider_value_style),
                                ],
                            ),
                            dcc.Slider(
                                id="units-slider",
                                min=1, max=2400, step=1, value=144,
                                marks=None,
                                tooltip={"always_visible": False},
                            ),
                        ]),

                        # Profit per unit — label updates with product name
                        html.Div([
                            html.Div(
                                style={"display": "flex", "justifyContent": "space-between", "marginBottom": "8px"},
                                children=[
                                    html.Span("Profit per Unit", id="profit-label", style=slider_label_style),
                                    html.Span("$280", id="profit-display", style=slider_value_style),
                                ],
                            ),
                            dcc.Slider(
                                id="profit-slider",
                                min=10, max=5000, step=5, value=280,
                                marks=None,
                                tooltip={"always_visible": False},
                            ),
                        ]),

                        # Breakdown
                        html.Div(
                            style={
                                "background": BG_MAIN, "borderRadius": "10px",
                                "padding": "1rem 1.25rem", "border": f"1px solid {BORDER}",
                            },
                            children=[
                                breakdown_row("Annual revenue (units × profit)", "b-ann-rev"),
                                breakdown_row("Investment cost",                 "b-inv"),
                                breakdown_row("Payback period",                  "b-payback"),
                                html.Div(
                                    [
                                        html.Span("12-month net gain", style={
                                            "color": WHITE, "fontSize": "14px", "fontWeight": "600",
                                        }),
                                        html.Span("—", id="b-net", style={
                                            "fontSize": "14px", "fontWeight": "700",
                                            "color": RED_MAIN, "fontVariantNumeric": "tabular-nums",
                                        }),
                                    ],
                                    style={
                                        "display": "flex", "justifyContent": "space-between",
                                        "alignItems": "center", "padding": "8px 0",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),

                # Right: metric cards + bar chart
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "1rem"},
                    children=[
                        html.Div(
                            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"},
                            children=[
                                metric_card("metric-ann-rev",    "Annual Revenue",    WHITE),
                                metric_card("metric-ann-profit", "Annual Net Profit", "#ffb3b0"),
                                metric_card("metric-roi",        "12-Month ROI",      RED_MAIN),
                                metric_card("metric-payback",    "Payback Period",    TEXT_MID),
                            ],
                        ),
                        html.Div(
                            style={**card_style, "flex": "1"},
                            children=[
                                html.Div("Revenue vs. Investment", style={**label_style, "marginBottom": "12px"}),
                                dcc.Graph(
                                    id="bar-chart",
                                    config={"displayModeBar": False},
                                    style={"height": "230px"},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),

        # ── CTA footer ────────────────────────────────────────────────────────
        html.Div(
            style={
                "maxWidth": "960px", "margin": "1.5rem auto 0",
                "display": "flex", "justifyContent": "flex-start",
                "alignItems": "center", "flexWrap": "wrap", "gap": "1rem",
            },
            children=[
                html.Div([
                    html.Span("Etherea Labs", style={
                        "color": WHITE, "fontWeight": "600", "fontSize": "14px",
                    }),
                    html.Span(" · ", style={"color": BORDER}),
                    html.Span(
                        "Premium Web Design & Development · Raleigh, NC",
                        style={"color": TEXT_MUTE, "fontSize": "13px"},
                    ),
                ]),
                html.A(
                    "Start your project →",
                    href="https://etherealabs.co/contact",
                    target="_blank",
                    style={
                        "background": RED_MAIN, "color": WHITE,
                        "padding": "10px 22px", "borderRadius": "8px",
                        "textDecoration": "none", "fontSize": "13px",
                        "fontWeight": "600", "letterSpacing": "0.02em",
                        "whiteSpace": "nowrap",
                    },
                ),
            ],
        ),
    ],
)


# ── Callback 1: tier dropdown / editable prices → investment slider ───────────
@callback(
    Output("inv-slider", "value"),
    Input("tier-dropdown",  "value"),
    Input("starter-price",  "value"),
    Input("growth-price",   "value"),
    State("inv-slider",     "value"),
)
def sync_tier(tier, starter_price, growth_price, current_inv):
    triggered     = ctx.triggered_id
    starter_price = starter_price or 809
    growth_price  = growth_price  or 1237

    if triggered == "tier-dropdown":
        if tier == "starter":
            return starter_price
        if tier == "growth":
            return growth_price
        return current_inv  # custom: leave slider where it is

    # price input changed — only update slider if that tier is active
    if triggered == "starter-price" and tier == "starter":
        return starter_price
    if triggered == "growth-price" and tier == "growth":
        return growth_price

    return current_inv


# ── Callback 2: main calc ─────────────────────────────────────────────────────
@callback(
    Output("inv-display",       "children"),
    Output("units-display",     "children"),
    Output("profit-display",    "children"),
    Output("units-label",       "children"),
    Output("profit-label",      "children"),
    Output("metric-ann-rev",    "children"),
    Output("metric-ann-profit", "children"),
    Output("metric-roi",        "children"),
    Output("metric-payback",    "children"),
    Output("b-ann-rev",         "children"),
    Output("b-inv",             "children"),
    Output("b-payback",         "children"),
    Output("b-net",             "children"),
    Output("bar-chart",         "figure"),
    Input("inv-slider",    "value"),
    Input("units-slider",  "value"),
    Input("profit-slider", "value"),
    Input("product-name",  "value"),
)
def update(inv, units, profit, product_name):
    def fmt(n):
        return f"${round(n):,}"

    product = (product_name or "Unit").strip() or "Unit"
    inv     = inv    or 0
    units   = units  or 0
    profit  = profit or 0

    ann_rev    = units * profit
    net_gain   = ann_rev - inv
    roi_pct    = (net_gain / inv * 100) if inv > 0 else 0
    payback_mo = (inv / (ann_rev / 12)) if ann_rev > 0 else float("inf")

    if payback_mo == float("inf"):
        payback_str = "N/A"
    elif payback_mo < 1:
        payback_str = "Under 1 month"
    elif payback_mo < 12:
        payback_str = f"{payback_mo:.1f} months"
    else:
        payback_str = f"{payback_mo / 12:.1f} years"

    # Dynamic labels using the product name
    units_label  = f"{product}s Sold per Year"
    profit_label = f"Profit per {product}"

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Investment", "Annual Revenue", "Net Gain"],
        y=[inv, ann_rev, net_gain],
        marker_color=[RED_SEC, RED_MAIN, "#ffb3b0"],
        marker_line_width=0,
        text=[fmt(inv), fmt(ann_rev), fmt(net_gain)],
        textposition="outside",
        textfont=dict(color=WHITE, size=12, family="Inter"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=0),
        font=dict(family="Inter", color=WHITE),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=TEXT_MID, size=11),
            linecolor=BORDER,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=BORDER, gridwidth=0.5,
            tickfont=dict(color=TEXT_MID, size=11),
            tickprefix="$", tickformat=",",
            linecolor="rgba(0,0,0,0)", zeroline=False,
        ),
        bargap=0.35,
        showlegend=False,
    )

    return (
        fmt(inv),
        f"{units:,}",
        fmt(profit),
        units_label,
        profit_label,
        fmt(ann_rev),
        fmt(net_gain),
        f"{round(roi_pct)}%",
        payback_str,
        fmt(ann_rev),
        f"−{fmt(inv)}",
        payback_str,
        fmt(net_gain),
        fig,
    )


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=4006)