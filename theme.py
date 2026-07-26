"""
theme.py — Shared design tokens and UI helpers.

Imported by both app.py and layout.py so neither has to import the other.
"""

import json
import os

from dash import dcc, html

# ── Default Configuration ─────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "product_name": "Website Package from Etherea Labs",
    "timeline_months": 12,
    "tiers": [
        {"name": "Starter Package",    "cost": 809,  "limit": 100},
        {"name": "Growth Package",     "cost": 1237, "limit": 500},
        {"name": "Enterprise Package", "cost": 5000, "limit": 999999}
    ],
    "brand": {
        "name": "Etherea Labs",
        "app_title": "Etherea Labs ROI Calculator",
        "initials": "EL",
        "site": "https://etherealabs.co/",
    },
    "colors": {
        "bg_page":   "#070101",   # near-black, slight red tint
        "bg_card":   "#130202",   # dark card background
        "bg_input":  "#0c0101",   # input fields
        "border":    "#2e0805",   # subtle border
        "border_hi": "#5a1208",   # highlighted border
        "red_main":  "#ff3428",   # vibrant accent
        "red_sec":   "#be0a00",   # deep accent
        "red_glow":  "#ff3428",
        "white":     "#ffffff",
        "text_hi":   "#ffffff",
        "text_mid":  "#c98080",   # mid-contrast label
        "text_mute": "#7a4848",   # muted label
        "green":     "#4ade80",   # bright accent for ROI
        "green_dim": "rgba(74, 222, 128, 0.08)"
    }
}


def load_config(path):
    """Load a settings JSON file and merge it over DEFAULT_CONFIG.

    Missing keys fall back to defaults so partial config files still work.
    """
    with open(path, "r") as f:
        overrides = json.load(f)
    cfg = {**DEFAULT_CONFIG, **overrides}
    cfg["tiers"] = overrides.get("tiers", DEFAULT_CONFIG["tiers"])
    cfg["brand"] = {**DEFAULT_CONFIG["brand"], **overrides.get("brand", {})}
    cfg["colors"] = {**DEFAULT_CONFIG["colors"], **overrides.get("colors", {})}
    return cfg


# ── Resolve initial config at import time ─────────────────────────────────────

CONFIGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs")
_CONFIG_FILE = os.environ.get("ROI_CONFIG_FILE")
INITIAL_CONFIG = load_config(_CONFIG_FILE) if _CONFIG_FILE else DEFAULT_CONFIG

# ── Brand Colors ──────────────────────────────────────────────────────────────

BG_PAGE   = INITIAL_CONFIG["colors"]["bg_page"]
BG_CARD   = INITIAL_CONFIG["colors"]["bg_card"]
BG_INPUT  = INITIAL_CONFIG["colors"]["bg_input"]
BORDER    = INITIAL_CONFIG["colors"]["border"]
BORDER_HI = INITIAL_CONFIG["colors"]["border_hi"]
RED_MAIN  = INITIAL_CONFIG["colors"]["red_main"]
RED_SEC   = INITIAL_CONFIG["colors"]["red_sec"]
RED_GLOW  = INITIAL_CONFIG["colors"]["red_glow"]
WHITE     = INITIAL_CONFIG["colors"]["white"]
TEXT_HI   = INITIAL_CONFIG["colors"]["text_hi"]
TEXT_MID  = INITIAL_CONFIG["colors"]["text_mid"]
TEXT_MUTE = INITIAL_CONFIG["colors"]["text_mute"]
GREEN     = INITIAL_CONFIG["colors"]["green"]
GREEN_DIM = INITIAL_CONFIG["colors"]["green_dim"]

# ── Brand Identity ────────────────────────────────────────────────────────────

BRAND_NAME     = INITIAL_CONFIG["brand"]["name"]
APP_TITLE      = INITIAL_CONFIG["brand"]["app_title"]
BRAND_INITIALS = INITIAL_CONFIG["brand"]["initials"]
BRAND_SITE     = INITIAL_CONFIG["brand"]["site"]


# ── Reusable UI Helpers ───────────────────────────────────────────────────────

def slider_row(label, slider_id, val_id, min_v, max_v, step_v, default_v):
    return html.Div(
        style={"display": "flex", "flexDirection": "column", "gap": "10px"},
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline"},
                children=[
                    html.Span(label, style={"fontSize": "12px", "fontWeight": "600", "letterSpacing": "0.04em",
                                            "color": TEXT_MID, "textTransform": "uppercase"}),
                    html.Span(id=val_id, style={"fontSize": "16px", "fontWeight": "800", "color": WHITE})
                ]
            ),
            dcc.Slider(id=slider_id, min=min_v, max=max_v, step=step_v, value=default_v,
                       marks=None, tooltip={"always_visible": False})
        ]
    )
