# Contributing

Thanks for considering contributing to this project. Here's how to get started.

## Development setup

```bash
git clone https://github.com/grizzleyyybear/anomaly-analog-detector.git
cd anomaly-analog-detector
npm install
cp .env.example .env.local   # add your Ably API key
npm run dev
```

For the ML pipeline:

```bash
cd ml
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python preflight.py
```

## Making changes

1. Create a feature branch from `main`
2. Make your changes
3. Run the checks:
   ```bash
   npm run lint
   npm run test
   npm run build
   ```
4. For ML changes:
   ```bash
   cd ml && python -m pytest tests/ -v
   ```
5. Commit with a descriptive message (pre-commit hooks will lint automatically)
6. Open a pull request against `main`

## Commit conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `test:` — adding or fixing tests
- `refactor:` — code change that neither fixes a bug nor adds a feature
- `chore:` — build process, dependencies, tooling

## Project structure

- `src/app/` — Next.js dashboard (React components, hooks, API routes)
- `ml/` — Python ML pipeline (models, training, inference)
- `ml/tests/` — pytest test suite for ML components
- `src/app/__tests__/` — Vitest test suite for dashboard components

## Code style

- **TypeScript** for all frontend code
- **Python 3.10+** for ML code
- Lint with ESLint (dashboard) — runs automatically on commit
- No unnecessary comments — code should be self-documenting

## Reporting issues

Open an issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Environment details (OS, Node version, Python version)
