# Contributing to DataHub Action: Glossary Export

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR-ORG/datahub-action-glossary-export.git
   cd datahub-action-glossary-export
   ```

2. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run tests:**
   ```bash
   make test
   ```

## Development Workflow

### Code Style

We use `ruff` for linting and formatting:

```bash
# Format code
make format

# Run linter
make lint

# Run type checker
make type-check
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_glossary_export_action.py -k test_name -v
```

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure tests pass:
   ```bash
   make all
   ```

3. Commit your changes with clear commit messages:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

4. Push to your fork and submit a pull request

## Pull Request Guidelines

- **Write tests** for new features and bug fixes
- **Update documentation** if you're changing functionality
- **Follow the existing code style** (enforced by ruff)
- **Keep commits atomic** and write clear commit messages
- **Add entries to CHANGELOG.md** for user-facing changes

## Reporting Issues

When reporting issues, please include:

- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (Python version, OS, DataHub version)
- **Configuration files** (sanitized of sensitive data)
- **Error messages and stack traces**

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read and follow it in all your interactions with the project.

## Questions?

If you have questions or need help, please:
- Open an issue for bugs or feature requests
- Check existing issues and documentation first
- Provide as much context as possible

Thank you for contributing! 🎉
