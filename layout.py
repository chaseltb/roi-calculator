


# ── Nav Bar ───────────────────────────────────────────────────────────────────
from dash import dcc, html

from theme import BG_CARD, BG_INPUT, BORDER, BORDER_HI, BRAND_INITIALS, BRAND_NAME, GREEN, RED_MAIN, RED_SEC, TEXT_MID, TEXT_MUTE, WHITE, slider_row


def nav_bar(current_path, embed=False):
    if embed:
        return None
    is_config = current_path == "/config"
    return html.Div(
        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center",
               "padding": "1.1rem 2rem", "borderBottom": f"1px solid {BORDER}", "marginBottom": "0"},
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "10px"},
                children=[
                    html.Div(
                        BRAND_INITIALS,
                        style={"width": "30px", "height": "30px", "borderRadius": "7px",
                               "background": f"linear-gradient(135deg, {RED_MAIN} 0%, {RED_SEC} 100%)",
                               "display": "flex", "alignItems": "center", "justifyContent": "center",
                               "fontSize": "15px", "fontWeight": "800", "color": WHITE,
                               "flexShrink": "0"}
                    ),
                    html.Span(BRAND_NAME,
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