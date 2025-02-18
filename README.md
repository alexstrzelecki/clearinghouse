# clearinghouse
API Server for making and clearing Schwab transactions

## Installation

Install `uv` package manager separately. Install dev dependencies:
```bash
uv sync
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
