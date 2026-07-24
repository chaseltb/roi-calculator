# Developer Guide

## Stack

- Single-page [Dash](https://dash.plotly.com/) app in [`app.py`](../app.py).
- Plotly (`plotly.graph_objects`) for the cumulative-return chart.
- No database — pricing config lives in a `dcc.Store(storage_type="session")`
  (`config-store`), so edits made via the `/config` page persist only for the
  visitor's browser tab/session, not globally or on disk.

`simple_calculator.py` is an earlier, standalone prototype of the same idea
(different styling, uses `dash-bootstrap-components`). It is not wired to
`app.py` and is kept for reference only.

## Routing

`dcc.Location` + a single `render_route` callback swap `page-content` between
two layouts based on `pathname`:

- `/` → `home_layout()` — the calculator dashboard (bento grid).
- `/config` → `config_layout()` — the settings form.

## Config shape

```json
{
  "product_name": "string, shown as the dashboard title",
  "timeline_months": 12,
  "tiers": [
    { "name": "string", "cost": 809,  "limit": 100 },
    { "name": "string", "cost": 1237, "limit": 500 },
    { "name": "string", "cost": 5000, "limit": 999999 }
  ]
}
```

- `tiers` must have exactly 3 entries (the UI hard-codes 3 tier rows).
- Tiers are matched by "Sales Per Year" against `limit`, in list order — the
  first tier whose `limit` is >= the slider value is the active tier. The
  last tier's `limit` should stay at (or above) `999999` to act as the
  uncapped/"Enterprise" tier.
- `DEFAULT_CONFIG` in `app.py` is the fallback config baked into the app.

## Loading a config file at startup

`load_config(path)` (in `app.py`) reads a JSON file and merges it over
`DEFAULT_CONFIG` (so a partial file, e.g. missing `timeline_months`, still
works — except `tiers`, which is replaced wholesale if present, since partial
tier lists don't make sense with the fixed 3-tier UI).

The app reads the `ROI_CONFIG_FILE` env var at import time and uses it to seed
`config-store`'s initial value:

```bash
ROI_CONFIG_FILE=configs/saas_onboarding.json python app.py
```

If unset, `DEFAULT_CONFIG` is used, matching prior behavior.

Note this only sets the *initial* value seen when the app boots — it does not
change what `/config` writes to. Users can still override it live via the
Configure page for their session; there is no server-side persistence layer.

### Adding a new demo config

1. Add a new JSON file to `configs/` following the shape above.
2. Add a row for it to the table in [`README.md`](../README.md).
3. Test it: `ROI_CONFIG_FILE=configs/your_file.json python app.py`.

## Calculation logic (`update_calculator`)

Given sliders `units` (sales/yr), `profit` (profit/sale), `conv` (%),
`traffic` (%):

```
new_units          = units * (1 + conv/100) * (1 + traffic/100)
incremental_annual = (new_units - units) * profit
net_benefit        = incremental_annual * (timeline_months / 12) - tier_cost
roi_pct            = net_benefit / tier_cost * 100
payback_months      = tier_cost / (incremental_annual / 12)
```

The cumulative-return chart plots `cash_flow[m] = -tier_cost + (incremental_annual/12) * m`
for `m` in `0..timeline_months`, shading the loss/profit zones and marking the
first month `cash_flow >= 0` as break-even.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `ROI_CONFIG_FILE` | Path to a JSON config file to seed initial pricing/timeline | unset → `DEFAULT_CONFIG` |
| `ROI_PORT` | Port to serve on | `4006` |

## Local dev

```bash
pip install dash plotly
python app.py          # debug=True, hot reload enabled
```

There is no test suite or build step; this is a single-file Dash app.
