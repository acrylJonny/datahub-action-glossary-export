# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-01-20

### Changed
- **Refactored codebase into modular structure** for better maintainability:
  - Split `glossary_export_action.py` (933 lines) into separate modules (934 lines total):
    - `config.py` (37 lines): Configuration models
    - `graphql.py` (418 lines): GraphQL queries and fetch operations
    - `snowflake.py` (201 lines): Snowflake database operations
    - `transformers.py` (141 lines): Data transformation functions
    - `glossary_export_action.py` (129 lines): Main action class
  - Removed verbose docstrings and copyright headers, keeping only essential documentation
  - All tests updated and passing (20 tests)

### Added
- **NEW FEATURE**: Glossary term usage tracking - Track where glossary terms are used across Power BI reports, Tableau dashboards, datasets, and other data assets
- New `usage_table_name` configuration parameter (default: `datahub_glossary_term_usage`)
- New `entity_types` configuration parameter to filter which entity types to track (default: `["DASHBOARD"]` for faster exports focused on reports)
- New Snowflake table for glossary term usage with composite primary key (glossary_term_urn, entity_urn)
- Support for tracking usage across multiple entity types: dashboards, charts, datasets, and data jobs
- Support for multiple platforms: Power BI, Tableau, Looker, Snowflake, BigQuery, Redshift, Databricks, dbt, and more
- GraphQL queries to fetch entities using specific glossary terms via `searchAcrossEntities`
- Usage data transformation including platform, entity subtype, container, and domain information
- Comprehensive test coverage for usage tracking functionality (19 tests total, all passing)
- New documentation: `docs/GLOSSARY_USAGE_GUIDE.md` with detailed use cases and examples
- New quick start guide: `docs/QUICKSTART_USAGE.md` for getting started in 5 minutes
- New GraphQL test file: `scripts/test_graphql_query.graphql` for testing queries against DataHub
- New SQL examples: `examples/example_usage_queries.sql` with 20+ example queries for analyzing glossary term usage
- Usage statistics and adoption tracking capabilities
- Impact analysis support - see which reports will be affected by term changes
- Governance checks - identify cross-domain term usage and orphaned terms

### Changed
- Updated README.md with usage table schema and query examples
- Enhanced examples/example_action.yaml with usage_table_name parameter
- Export process now includes two phases: glossary export and usage export
- Improved logging to show progress for each glossary term usage fetch

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
