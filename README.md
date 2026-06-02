# Smart Waste Management

A premium **Frappe/ERPNext** custom app that provides:

- Complete waste‑category, zone, vehicle, driver, route, and invoice management
- AI‑driven waste‑forecasting (scikit‑learn LinearRegression) and route suggestions
- Four polished script reports with Plotly visualisations
- A glass‑morphism dashboard page (`waste_dashboard`) with KPI cards and interactive charts
- Installation fixtures that seed default categories, zones, and custom fields on ERPNext standard DocTypes

## Quick Install

```bash
# 1️⃣ Ensure Bench/ERPNext v15+ is installed
pip3 install --upgrade frappe-bench

# 2️⃣ Create a bench (or use an existing one)
bench init waste-bench --frappe-branch version-15
cd waste-bench

# 3️⃣ Create a site
bench new-site waste.local   # set MySQL root & admin passwords when prompted

# 4️⃣ Get the app from GitHub
bench get-app https://github.com/balaji-001-gif/waste_management.git

# 5️⃣ Install the app on the site
bench --site waste.local install-app waste_management

# 6️⃣ Start the dev server and open the site
bench start      # then open http://waste.local:8000 in a browser
```

The **Waste Management** module appears on the desktop. Open **Waste Dashboard** for the premium UI.

## Development

- Run `bench watch` to hot‑reload JS/CSS.
- The AI engine lives in `waste_management/waste_management/ai/waste_ai_engine.py`.
- Add custom fixtures under `fixtures/` if you need sample data.

## Testing & CI

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs:
- `bench setup requirements`
- `pytest` for unit tests placed in `tests/`
- `flake8` linting.

## Contributing

See `CONTRIBUTING.md` for guidelines on pull requests, coding style, and testing.

## License

MIT © 2026 Balaji K.
