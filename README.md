# clearinghouse
API Server for making and clearing Schwab transactions

## Installation

Install `uv` package manager separately. Install dev dependencies:
```bash
uv sync
```

Install the pre-commit hook:
```bash
pre-commit install
```

Setup envvar for secrets or use a dotfile (`.env`) with the same variables.
`.env` file will be used before envvar if both are present.
```bash
export SCHWAB_APP_KEY="<insert value here>"
export SCHWAB_APP_SECRET="<insert value here>"
```

## Usage
Run the dev server with the following:
```bash
uv run fastapi dev clearinghouse/main.py
```

## Testing
Run all tests with
```bash
uv run -m pytest
```
