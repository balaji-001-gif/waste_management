# Contributing to Smart Waste Management

Thank you for considering a contribution! 🎉

## Prerequisites
- Python 3.11+
- Bench (`pip install frappe-bench`)
- A local ERPNext site (see the README)

## Quick start
```bash
git clone https://github.com/balaji-001-gif/waste_management.git
cd waste_management
bench get-app .
bench --site <your-site> install-app waste_management
```

## Development workflow
1. **Create a branch**
   ```bash
   git checkout -b feature/awesome-thing
   ```
2. **Write code + tests**
   Keep the test suite green: `pytest`.
3. **Run linters**
   ```bash
   pre-commit run --all-files   # or `ruff .`
   ```
4. **Commit & push**
   Follow conventional commits (`feat:`, `fix:`, `docs:` …).
5. **Open a Pull Request**
   The CI will run automatically.

## Code style
- Black (line length 88)
- Ruff for linting (`ruff check .`)
- Type hints are encouraged (`mypy`).

## Reporting bugs
Please open an issue with:
- A clear title
- Steps to reproduce
- Expected vs. actual behavior
- Screenshots (if UI related).

Happy hacking! 🚀
