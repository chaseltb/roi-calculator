"""
theme.py — Shared design tokens and UI helpers.

Imported by both app.py and layout.py so neither has to import the other.
"""

import json
import os
import re as _re

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
    },
    # Slider label overrides — any key omitted falls back to the value below
    "sliders": {
        "units_label":      "Current Sales Per Year",
        "profit_label":     "Profit Per Sale",
        "conversion_label": "Conversion Boost",
        "traffic_label":    "SEO Traffic Growth",
    },
    # When True the units slider represents *additional* sales directly,
    # bypassing the conversion/traffic multiplier step.
    "additional_sales_mode": False,
}


_COLOR_RE = _re.compile(
    r"^(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|hsla?\([^)]+\)|[a-z]+)$"
)


def _is_valid_color(value):
    """Return True if *value* looks like a CSS colour string."""
    return isinstance(value, str) and bool(_COLOR_RE.match(value.strip()))


def _merge_colors(overrides_raw):
    """Key-by-key merge of the colours dict, falling back per invalid entry."""
    defaults = DEFAULT_CONFIG["colors"]
    raw = overrides_raw if isinstance(overrides_raw, dict) else {}
    merged = {}
    for key, default_val in defaults.items():
        candidate = raw.get(key, default_val)
        if _is_valid_color(candidate):
            merged[key] = candidate
        else:
            merged[key] = default_val  # bad/missing value → use default
    return merged


def _merge_brand(overrides_raw):
    """Key-by-key merge of the brand dict, falling back per invalid entry."""
    defaults = DEFAULT_CONFIG["brand"]
    raw = overrides_raw if isinstance(overrides_raw, dict) else {}
    merged = {}
    for key, default_val in defaults.items():
        candidate = raw.get(key, default_val)
        # brand values must be non-empty strings
        if isinstance(candidate, str) and candidate.strip():
            merged[key] = candidate
        else:
            merged[key] = default_val
    return merged


def _merge_sliders(overrides_raw):
    """Key-by-key merge of slider labels, falling back per invalid entry."""
    defaults = DEFAULT_CONFIG["sliders"]
    raw = overrides_raw if isinstance(overrides_raw, dict) else {}
    merged = {}
    for key, default_val in defaults.items():
        candidate = raw.get(key, default_val)
        if isinstance(candidate, str) and candidate.strip():
            merged[key] = candidate.strip()
        else:
            merged[key] = default_val
    return merged


def _merge_tiers(overrides_raw):
    """Validate each tier dict; fall back to the matching default tier on error."""
    defaults = DEFAULT_CONFIG["tiers"]
    raw = overrides_raw if isinstance(overrides_raw, list) else []
    if not raw:
        return defaults

    merged = []
    for i, default_tier in enumerate(defaults):
        raw_tier = raw[i] if i < len(raw) else {}
        if not isinstance(raw_tier, dict):
            merged.append(default_tier)
            continue

        name = raw_tier.get("name", default_tier["name"])
        cost = raw_tier.get("cost", default_tier["cost"])
        limit = raw_tier.get("limit", default_tier["limit"])

        # name must be a non-empty string
        if not (isinstance(name, str) and name.strip()):
            name = default_tier["name"]

        # cost must be a non-negative number
        try:
            cost = float(cost)
            if cost < 0:
                raise ValueError
        except (TypeError, ValueError):
            cost = default_tier["cost"]

        # limit must be a positive integer (last tier may be 999999)
        try:
            limit = int(limit)
            if limit <= 0:
                raise ValueError
        except (TypeError, ValueError):
            limit = default_tier["limit"]

        merged.append({"name": name, "cost": cost, "limit": limit})

    return merged


def load_config(path):
    """Load a JSON config file and deep-merge it over DEFAULT_CONFIG.

    Every field is validated individually; anything missing or invalid
    silently falls back to the corresponding default — no KeyError possible.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            overrides = json.load(f)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()

    if not isinstance(overrides, dict):
        return DEFAULT_CONFIG.copy()

    # Top-level scalar fields
    product_name = overrides.get("product_name", DEFAULT_CONFIG["product_name"])
    if not (isinstance(product_name, str) and product_name.strip()):
        product_name = DEFAULT_CONFIG["product_name"]

    timeline = overrides.get("timeline_months", DEFAULT_CONFIG["timeline_months"])
    try:
        timeline = int(timeline)
        if not (1 <= timeline <= 120):
            raise ValueError
    except (TypeError, ValueError):
        timeline = DEFAULT_CONFIG["timeline_months"]

    # additional_sales_mode must be an explicit boolean
    asm = overrides.get("additional_sales_mode", DEFAULT_CONFIG["additional_sales_mode"])
    if not isinstance(asm, bool):
        asm = DEFAULT_CONFIG["additional_sales_mode"]

    return {
        "product_name":         product_name,
        "timeline_months":      timeline,
        "tiers":                _merge_tiers(overrides.get("tiers")),
        "brand":                _merge_brand(overrides.get("brand")),
        "colors":               _merge_colors(overrides.get("colors")),
        "sliders":              _merge_sliders(overrides.get("sliders")),
        "additional_sales_mode": asm,
    }


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

def slider_row(label, slider_id, val_id, min_v, max_v, step_v, default_v, label_id=None):
    """Render a labelled slider row.

    Pass *label_id* to make the label span reactive (updatable via callback).
    """
    span_extra = {"id": label_id} if label_id else {}
    return html.Div(
        style={"display": "flex", "flexDirection": "column", "gap": "10px"},
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "baseline"},
                children=[
                    html.Span(label, **span_extra,
                              style={"fontSize": "12px", "fontWeight": "600", "letterSpacing": "0.04em",
                                     "color": TEXT_MID, "textTransform": "uppercase"}),
                    html.Span(id=val_id, style={"fontSize": "16px", "fontWeight": "800", "color": WHITE})
                ]
            ),
            dcc.Slider(id=slider_id, min=min_v, max=max_v, step=step_v, value=default_v,
                       marks=None, tooltip={"always_visible": False})
        ]
    )
