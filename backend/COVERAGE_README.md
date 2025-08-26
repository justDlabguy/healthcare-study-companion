# Test Coverage Configuration

This document describes the test coverage setup for the Healthcare Study Companion backend.

## Overview

The project uses `coverage.py` with `pytest-cov` to measure test coverage. Coverage reporting is integrated into both local development and CI/CD pipelines.

## Configuration Files

### `.coveragerc`

Main configuration file for coverage.py with the following settings:

- **Source**: Measures coverage for the `app` package
- **Omit**: Excludes test files, migrations, scripts, and configuration files
- **Branch Coverage**: Enabled for more comprehensive coverage analysis
- **Minimum Coverage**: 80% threshold
- **Reports**: Generates HTML, XML, JSON, and terminal reports

### `pytest.ini`

Pytest configuration includes coverage options:

- `--cov=app`: Measure coverage for app package
- `--cov-report=term-missing`: Show missing lines in terminal
- `--cov-report=html`: Generate HTML report
- `--cov-report=xml`: Generate XML report for CI/CD
- `--cov-report=json`: Generate JSON report for programmatic access
- `--cov-branch`: Enable branch coverage
- `--cov-fail-under=80`: Fail if coverage below 80%

## Running Coverage Locally

### Quick Start

```bash
# Run tests with coverage (simple)
python run_coverage.py

# Run tests with coverage (using pytest directly)
pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file with coverage
pytest tests/test_vector_search.py --cov=app --cov-report=term-missing
```

### Using Coverage Configuration Script

```bash
# Run all tests with coverage
python scripts/coverage_config.py test

# Run specific test path
python scripts/coverage_config.py test --test-path tests/test_vector_search.py

# Generate specific report format
python scripts/coverage_config.py report --format html

# Check coverage threshold
python scripts/coverage_config.py check --min-coverage 85

# Get coverage summary
python scripts/coverage_config.py summary

# Clean coverage files
python scripts/coverage_config.py clean
```

## Coverage Reports

### Terminal Report

Shows coverage percentage and missing lines directly in the terminal:

```
Name                                 Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------
app/services/vector_search.py          45      5     12      2    85%   23-25, 67-69
app/services/document_processor.py     38      3      8      1    89%   45-47
--------------------------------------------------------------------------------
TOTAL                                  83      8     20      3    87%
```

### HTML Report

Interactive HTML report generated in `htmlcov/` directory:

- Open `htmlcov/index.html` in browser
- Click on files to see line-by-line coverage
- Highlights covered, uncovered, and partially covered lines

### XML Report

Machine-readable XML format (`coverage.xml`) used by CI/CD systems and coverage tools.

### JSON Report

Programmatic access to coverage data (`coverage.json`) for custom analysis.

## CI/CD Integration

### GitHub Actions

The backend CI workflow (`.github/workflows/backend-ci.yml`) includes:

- Runs tests with coverage reporting
- Uploads coverage reports as artifacts
- Adds coverage comments to pull requests
- Fails build if coverage below 80%

### Coverage Artifacts

CI/CD uploads the following artifacts:

- `coverage.xml`: For coverage services integration
- `htmlcov/`: HTML report directory
- `coverage.json`: JSON data for analysis

## Coverage Thresholds

### Current Settings

- **Minimum Coverage**: 80%
- **Branch Coverage**: Enabled
- **Fail Under**: Tests fail if coverage drops below threshold

### Adjusting Thresholds

To change coverage requirements:

1. **pytest.ini**: Update `--cov-fail-under=XX`
2. **.coveragerc**: No specific threshold setting needed
3. **CI/CD**: Update `MINIMUM_GREEN` and `MINIMUM_ORANGE` in workflow
4. **Scripts**: Update default `min_coverage` parameter

## Excluded Files

The following files/directories are excluded from coverage:

- `*/tests/*` - Test files themselves
- `*/test_*` - Test files
- `*/conftest.py` - Pytest configuration
- `*/migrations/*` - Database migrations
- `*/alembic/*` - Alembic migration files
- `*/scripts/*` - Utility scripts
- `app/main.py` - FastAPI application entry point
- `app/config.py` - Configuration file

## Best Practices

### Writing Testable Code

- Keep functions small and focused
- Avoid complex nested conditions
- Use dependency injection for external services
- Separate business logic from framework code

### Improving Coverage

1. **Identify Missing Coverage**:

   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

2. **Focus on Critical Paths**:

   - Business logic functions
   - Error handling paths
   - Edge cases

3. **Use Coverage Reports**:
   - HTML report shows exact missing lines
   - Branch coverage identifies unhandled conditions

### Coverage Goals

- **80%+ Overall**: Minimum acceptable coverage
- **90%+ Business Logic**: Core functionality should be well-tested
- **100% Critical Paths**: Authentication, data processing, etc.

## Troubleshooting

### Common Issues

1. **Coverage Not Found**:

   ```bash
   # Ensure pytest-cov is installed
   pip install pytest-cov
   ```

2. **Low Coverage Warnings**:

   - Check excluded files in `.coveragerc`
   - Verify test files are being discovered
   - Run with `-v` flag for detailed output

3. **Branch Coverage Issues**:
   - Enable branch coverage: `--cov-branch`
   - Check for unhandled if/else conditions
   - Test both True and False paths

### Debugging Coverage

```bash
# Run with verbose output
pytest --cov=app --cov-report=term-missing -v

# Show coverage for specific module
pytest tests/test_vector_search.py --cov=app.services.vector_search --cov-report=term-missing

# Generate detailed HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Integration with Development Workflow

### Pre-commit Hooks

Consider adding coverage checks to pre-commit hooks:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: pytest-coverage
      name: pytest-coverage
      entry: pytest --cov=app --cov-fail-under=80
      language: system
      pass_filenames: false
```

### IDE Integration

Most IDEs support coverage visualization:

- **VS Code**: Python extension shows coverage in gutter
- **PyCharm**: Built-in coverage runner and visualization
- **Vim/Neovim**: Coverage plugins available

## Monitoring Coverage Over Time

### Coverage Trends

- Track coverage percentage in CI/CD
- Set up alerts for coverage drops
- Review coverage reports in code reviews

### Coverage Goals

- Maintain or improve coverage with each PR
- Focus on testing new features thoroughly
- Refactor to improve testability when coverage is low
