# Repository Guidelines

## Project Structure & Module Organization
- `walk_risk/core/` retains gameplay logic (risk puzzles, tutorials, trading) while `services/` exposes those flows via API-ready classes and `api/` hosts the FastAPI wiring.
- Mentor personas, demos, and docs remain in `ai/`, root-level `*_demo.py`, and `docs/`; keep Korean narrative text intact when touching them.
- Data adapters live in `data/market_data/` and share models with `walk_risk/models/`; do not bypass these layers when adding integrations.

## Build, Test, and Development Commands
```bash
uv sync                                   # sync deps (uv only; no pip/conda)
uv run python api_server.py               # launch FastAPI server (lifespan bootstraps services)
uv run python integrated_tutorial_demo.py # full puzzle+tutorial walkthrough
uv run python risk_puzzle_auto_demo.py    # automated puzzle regression
uv run python tutorial_auto_demo.py       # legacy tutorial reference
```
- Add or trim packages strictly via `uv add`, `uv add --dev`, `uv remove`; rerun `uv sync` after manifest changes.

## Coding Style & Naming Conventions
- Python 3.12+, four-space indentation, snake_case, and exhaustive type hints mirroring existing service signatures.
- Prefer async/await when touching IO paths, log via `setup_logger`, and preserve Korean copy and emoji styling in user-facing output.
- Format with Black and lint with Ruff (`uv add --dev black ruff`) before raising PRs.

## Testing Guidelines
- House automated tests in `tests/`, mirroring modules (`tests/services/test_puzzle_service.py`, etc.) with `pytest` and `pytest.mark.asyncio` for coroutine paths.
- Stub Yahoo Finance interactions in fixtures; pair test runs with demo scripts to confirm Rich CLI flows still render correctly.

## Commit & Pull Request Guidelines
- Use imperative, scope-first commits (`services: refine hypothesis validation`) and describe rationale, risks, and any follow-up tasks in the body.
- PRs must list verification commands (`uv run python api_server.py`, `uv run python integrated_tutorial_demo.py`) and reference development logs or roadmap items they affect.
- Update affected docs (`docs/roadmap_next_steps.md`, `CLAUDE.md`, `readme.md`) when behaviour or workflow expectations change.

## Session Workflow & Documentation
- Begin each session by reviewing `docs/development_log_*.md | tail -50` and `docs/roadmap_next_steps.md`, then run the core demos above to confirm baseline health.
- Capture decisions, blockers, and partial outcomes as you work; end the session by writing a dated development log, adjusting the roadmap, and appending any enduring guidance to `CLAUDE.md`.
- Treat every change as an educational enhancement: ask whether it keeps risk-as-puzzle gameplay intact, leverages real market data, and supports collaborative learning.
