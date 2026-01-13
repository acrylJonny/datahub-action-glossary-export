# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of DataHub Action: Glossary Export
- Export DataHub glossary terms and nodes to Snowflake
- Support for all Snowflake authentication methods (password, key pair, OAuth, SSO)
- Hierarchical path construction for glossary terms
- Domain association tracking
- Ownership information (technical and business owners)
- Custom properties support
- Comprehensive documentation and examples
- Full test coverage
- Linting with ruff and mypy
- GitHub Actions CI/CD workflows
- Makefile for common development tasks
- Explicit SQLAlchemy dependency (required by Snowflake connector)

### Changed
- **BREAKING**: Dropped Python 3.8 support (now requires Python 3.9+)
- Modernized type hints to use built-in `dict` and `list` instead of `typing.Dict` and `typing.List`
- Updated CI/CD workflow to test Python 3.9, 3.10, and 3.11 (Python 3.12 not yet supported by DataHub)
- Replaced flake8 and black with ruff for linting and formatting
- Improved GitHub Actions workflow to match development tools

## [0.1.0] - TBD

### Added
- First public release
