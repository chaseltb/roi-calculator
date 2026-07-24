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
4. It's now also loadable per-request via `?config=<filename-without-.json>`
   (see [Embedding](#embedding) below) — no server restart needed.

## Embedding

Two URL query params control embed behavior, read in `render_route` /
`seed_config_from_query`:

- `embed=1` — `home_layout(embed=True)` skips rendering `nav_bar` and tightens
  page padding, so the app reads as a widget rather than a standalone site.
- `config=<slug>` — resolved by `load_config_by_slug(slug)`, which maps the
  slug to `configs/<slug>.json`. This is deliberately narrow: no path
  separators or `..` are allowed, and the resolved path is checked to still be
  inside `CONFIGS_DIR`, so it can't be used to read arbitrary files off disk.
  An invalid/missing slug silently falls back to whatever's already in
  `config-store` (or `DEFAULT_CONFIG`) rather than erroring — this callback
  uses `Output("config-store", "data", allow_duplicate=True)` since
  `manage_config` (the Configure-page save/reset callback) also targets that
  store; both are marked `prevent_initial_call` so the two never race on load.

### Framing / CSP

By default Flask/Dash doesn't send `X-Frame-Options`, but some proxies or
`flask-talisman`-style setups do — `_allow_embedding` (an `after_request` hook
in `app.py`) explicitly strips `X-Frame-Options` and sets
`Content-Security-Policy: frame-ancestors <value>` on every response. Control
the allowed embedding origins with `ROI_FRAME_ANCESTORS` (space-separated
origins); it defaults to `*` (embeddable anywhere), which is fine for demos
but should be locked down per-client in production, e.g.:

```bash
ROI_FRAME_ANCESTORS="https://etherealabs.com https://client-site.com" python app.py
```

### Auto-resizing iframes

A small inline script in `index_string` detects it's running inside an
`<iframe>` (`window.self !== window.top`), watches `document.body` with a
`MutationObserver`, and `postMessage`s `{type: "roi-calculator:height", height}`
to the parent whenever the rendered height changes. Host pages can listen for
it to avoid a fixed iframe height:

```html
<script>
  window.addEventListener("message", (e) => {
    if (e.data?.type === "roi-calculator:height") {
      document.getElementById("roi-iframe").style.height = e.data.height + "px";
    }
  });
</script>
```

If you don't wire this up, embedders should just set a reasonably tall fixed
`height` on the iframe (~900px covers the desktop bento layout).

## Input validation

`manage_config` (the Configure-page save handler) rejects and reports, without
touching the stored config, on:

- Missing product name or timeline.
- Non-numeric cost/limit/timeline fields.
- Timeline outside `1..120` months.
- Negative costs.
- Tier 1 limit `<= 0`, or Tier 2 limit `<=` Tier 1 limit (tiers must be
  strictly increasing so the "first tier whose limit is >= units" matching in
  `update_calculator` behaves sensibly).

There's intentionally no validation on the calculator sliders themselves —
`dcc.Slider` `min`/`max`/`step` already constrain those inputs at the widget
level.

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
| `ROI_FRAME_ANCESTORS` | Space-separated origins allowed to `<iframe>`-embed the app (`Content-Security-Policy: frame-ancestors`) | `*` |

## Local dev

```bash
pip install -r requirements.txt
python app.py          # debug=True, hot reload enabled
```

There is no test suite or build step; this is a single-file Dash app.

## Deployment

`app.py` exposes the underlying Flask app as a module-level `server` variable
(`server = app.server`), so it can run under any WSGI server instead of Dash's
built-in dev server:

```bash
gunicorn --bind 0.0.0.0:4006 --workers 2 app:server
```

A [`Dockerfile`](../Dockerfile) is included and does exactly this. Build/run:

```bash
docker build -t roi-calculator .
docker run -p 4006:4006 \
  -e ROI_CONFIG_FILE=configs/etherea_default.json \
  -e ROI_FRAME_ANCESTORS="https://etherealabs.com" \
  roi-calculator
```

`debug=True` in the `__main__` block only applies to `python app.py` directly
— gunicorn/Docker never hit that code path, so hot reload and the Dash
debug/error overlay are automatically off in that deployment.
