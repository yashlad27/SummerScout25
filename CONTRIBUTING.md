# Contributing to Job Tracker

Thank you for contributing to the Summer 2026 Internship Job Tracker!

## Adding a New ATS Scraper

1. **Create scraper file**: `src/ingest/ats/youratsname.py`

```python
from src.ingest.base import BaseScraper
from src.ingest.schemas import RawJob, WatchlistTarget

class YourATSScraper(BaseScraper):
    source = "youratsname"
    
    def fetch(self) -> list[RawJob]:
        # Implement fetching logic
        pass
```

2. **Register scraper**: Add to `src/ingest/registry.py`

```python
from src.ingest.ats.youratsname import YourATSScraper

SCRAPER_REGISTRY = {
    # ... existing
    "youratsname": YourATSScraper,
}
```

3. **Test the scraper**:

```bash
poetry run python -m src.ingest.runner --dry-run --company "TestCompany"
```

4. **Add tests**: Create `tests/test_youratsname.py`

## Adding a New Category

Edit `config/filters.yaml`:

```yaml
categories:
  your_category:
    title_any:
      - "(?i)keyword1"
      - "(?i)keyword2"
    description_hints:
      - "(?i)hint1"
      - "(?i)hint2"
```

## Code Style

- Run Black for formatting: `make format`
- Run Ruff for linting: `make lint`
- Follow existing patterns
- Add docstrings to public functions
- Keep functions focused and small

## Testing

- Write tests for new features
- Ensure tests pass: `make test`
- Use fixtures from `tests/conftest.py`

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Update documentation
5. Submit PR with clear description

## Questions?

Open an issue or reach out to the maintainers.
