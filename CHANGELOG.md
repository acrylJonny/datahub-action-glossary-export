# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-01-13

### Changed
- **BREAKING**: Dropped Python 3.8 support (now requires Python 3.9+)
- Moved `acryl-datahub` and `acryl-datahub-actions` to optional dev dependencies to avoid conflicts with DataHub Cloud
- Removed Python 3.12 from CI/CD (not yet supported by DataHub)
- Modernized type hints to use built-in `dict` and `list` instead of `typing.Dict` and `typing.List`
- Updated documentation with correct DataHub Cloud deployment instructions

### Added
- Explicit SQLAlchemy dependency (required by Snowflake connector)
- Documentation for wheel-based deployment to DataHub Cloud

### Fixed
- Dependency conflicts when deploying to DataHub Cloud
- GitHub Actions release workflow permissions
- Mypy configuration to properly handle dev dependencies

## [0.1.2] - 2026-01-13

### Fixed
- Added GitHub release permissions to CI/CD workflow
- Removed PyPI publishing step (not needed for DataHub Cloud)

## [0.1.1] - 2026-01-13

### Changed
- Removed `setup.py` in favor of modern `pyproject.toml` packaging
- Updated license format to SPDX standard string

## [0.1.0] - 2026-01-13

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
