# Etherea ROI Calculator

An interactive ROI calculator built with [Dash](https://dash.plotly.com/). Prospects
drag a few sliders describing their business and instantly see projected ROI,
payback period, extra annual profit, and a cumulative-return chart against your
pricing tiers.

## Using the calculator

1. Open the app in your browser (your team will give you the URL, or run it
   locally — see [Running it yourself](#running-it-yourself)).
2. On the main dashboard, adjust the sliders under **Your Business**:
   - **Sales Per Year** — how many sales/customers you close annually today.
   - **Profit Per Sale** — your average profit per sale.
   And under **Projected Gains**:
   - **Conversion Boost** — expected % lift in conversion rate.
   - **SEO Traffic Growth** — expected % growth in traffic.
3. The right-hand cards update live:
   - **Return on Investment** — net return as a percentage of the package cost.
   - **Payback Period** — how many months until the investment pays for itself.
   - **Extra Annual Profit** — additional profit generated over the configured
     timeline.
   - **Cumulative Return** chart — shows cash flow over time, with a
     break-even marker.
4. Your sales volume automatically selects a pricing tier (shown at the bottom
   of the inputs card) based on the volume limits configured for that demo.

### Configuring pricing (no code required)

Click **⚙ Configure** in the top-right to open the settings page:

- **Product / Service Name** — the title shown on the dashboard.
- **Timeline (Months)** — the projection horizon used everywhere on the
  dashboard.
- **Pricing Tiers** — up to three tiers, each with a name, cost, and a sales
  volume limit (the 3rd tier is always uncapped/"Unlimited").

Click **Save Configuration** to apply changes for your current browser
session, or **Reset to Defaults** to restore the built-in defaults. Changes
made here only last for your current session/tab — they are not written back
to disk. To make a configuration permanent, see the developer docs.

## Running it yourself

Requires Python 3.9+.

```bash
pip install dash plotly
python app.py
```

Then open http://localhost:4006 in your browser.

### Loading a demo configuration

The [`configs/`](configs/) folder has a few ready-made pricing setups you can
load without touching the Configure page. Point the app at one with the
`ROI_CONFIG_FILE` environment variable:

```bash
# macOS/Linux
ROI_CONFIG_FILE=configs/marketing_agency.json python app.py

# Windows PowerShell
$env:ROI_CONFIG_FILE = "configs/marketing_agency.json"; python app.py
```

Available demo configs:

| File | Scenario |
|---|---|
| `configs/etherea_default.json` | Etherea's own website platform (default) |
| `configs/marketing_agency.json` | Marketing retainer tiers |
| `configs/saas_onboarding.json` | SaaS onboarding automation product |
| `configs/ecommerce_conversion.json` | E-commerce conversion audit/rebuild service |

See [`docs/DEVELOPER.md`](docs/DEVELOPER.md) for the config file format,
architecture notes, and how to add your own.
