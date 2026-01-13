# Project Structure

This document provides an overview of the project structure and file organization.

## Directory Tree

```
datahub-action-glossary-export/
├── .github/
│   └── workflows/
│       ├── test.yml              # CI pipeline for running tests
│       └── release.yml           # Release pipeline for publishing
├── action_glossary_export/
│   ├── __init__.py               # Package initialization
│   └── glossary_export_action.py # Main action implementation
├── tests/
│   ├── __init__.py               # Test package initialization
│   └── test_glossary_export_action.py  # Unit tests
├── .gitattributes                # Git line ending configuration
├── .gitignore                    # Git ignore patterns
├── DEPLOYMENT.md                 # DataHub Cloud deployment guide
├── LICENSE                       # Apache 2.0 license
├── PROJECT_STRUCTURE.md          # This file
├── QUICKSTART.md                 # Quick start guide (5-minute setup)
├── README.md                     # Main documentation
├── SUMMARY.md                    # Comprehensive project overview
├── example_action.yaml           # Example configuration file
├── example_queries.sql           # 30+ example SQL queries
├── requirements.txt              # Python dependencies
└── setup.py                      # Package installation config
```

## Core Files

### Action Implementation

- **`action_glossary_export/glossary_export_action.py`** (585 lines)
  - Main action class: `GlossaryExportAction`
  - Configuration models: `SnowflakeConfig`, `GlossaryExportConfig`
  - Methods:
    - `export_glossary()` - Main export orchestration
    - `_fetch_all_glossary_terms()` - GraphQL query for terms
    - `_fetch_all_glossary_nodes()` - GraphQL query for nodes
    - `_transform_entity_to_row()` - Data transformation
    - `_insert_rows_to_snowflake()` - Database operations
    - `_get_snowflake_connection()` - Connection management
    - `_create_table_if_not_exists()` - Table schema creation

### Configuration

- **`setup.py`** (55 lines)
  - Package metadata
  - Dependencies: acryl-datahub-actions, snowflake-connector-python, pydantic
  - Entry point registration: `action-glossary-export`
  - Python version requirements: >=3.8

- **`example_action.yaml`** (31 lines)
  - Complete action configuration example
  - Shows all configuration options
  - Environment variable usage
  - Both local and DataHub Cloud compatible

### Testing

- **`tests/test_glossary_export_action.py`** (293 lines)
  - 15+ unit tests covering:
    - Configuration validation
    - Action creation
    - Database connection
    - Data transformation
    - GraphQL queries
    - Table operations
  - Uses pytest and mocking

- **`requirements.txt`** (17 lines)
  - Production dependencies
  - Development/testing dependencies
  - Version constraints

### Documentation

- **`README.md`** (379 lines)
  - Complete user documentation
  - Installation instructions
  - Configuration reference
  - Output schema
  - Usage examples
  - Troubleshooting

- **`QUICKSTART.md`** (147 lines)
  - Fast-track setup guide
  - Two deployment options
  - Basic queries
  - Quick troubleshooting

- **`DEPLOYMENT.md`** (283 lines)
  - DataHub Cloud deployment walkthrough
  - Step-by-step instructions
  - Secret management
  - Monitoring and verification
  - Advanced configurations

- **`SUMMARY.md`** (408 lines)
  - Comprehensive project overview
  - Feature list
  - Data model explanation
  - Use cases
  - Customization ideas

- **`example_queries.sql`** (392 lines)
  - 30+ SQL queries organized by category:
    - Basic queries (5)
    - Hierarchy analysis (5)
    - Domain analysis (4)
    - Ownership analysis (5)
    - Custom properties (3)
    - Search and discovery (3)
    - Data quality checks (3)
    - Reporting (3)

### CI/CD

- **`.github/workflows/test.yml`**
  - Automated testing on push/PR
  - Matrix testing: Python 3.8, 3.9, 3.10, 3.11
  - Code coverage reporting
  - Linting with flake8
  - Formatting checks with black
  - Type checking with mypy

- **`.github/workflows/release.yml`**
  - Automated releases on version tags
  - Build and package creation
  - GitHub release creation
  - Optional PyPI publishing

### Supporting Files

- **`.gitignore`** - Excludes build artifacts, credentials, IDE files
- **`.gitattributes`** - Ensures LF line endings for cross-platform compatibility
- **`LICENSE`** - Apache 2.0 license text

## Key Components

### 1. Action Framework Integration

The action integrates with DataHub Actions framework via:
- Entry point: `datahub_actions.action.plugins`
- Base class: `Action` from `datahub_actions.action.action`
- Context: `PipelineContext` with access to DataHub graph

### 2. Data Flow

```
DataHub GraphQL API
        ↓
  Fetch Terms & Nodes
        ↓
  Transform to Rows
        ↓
 Snowflake Connector
        ↓
  Insert into Table
```

### 3. Configuration Flow

```
YAML Config File
        ↓
  Pydantic Validation
        ↓
  GlossaryExportConfig
        ↓
  Action Initialization
        ↓
  Export Execution
```

## Code Statistics

- **Total Lines**: ~2,800 (including docs)
- **Python Code**: ~900 lines
- **Documentation**: ~1,600 lines
- **SQL Queries**: ~400 lines
- **Tests**: ~300 lines

## Dependencies

### Production
- `acryl-datahub-actions` - DataHub Actions framework
- `acryl-datahub` - DataHub Python SDK
- `snowflake-connector-python` - Snowflake database driver
- `pydantic` - Data validation and settings

### Development
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## Design Patterns

### 1. Factory Pattern
- `create()` class method for action instantiation
- Validates configuration before creating instance

### 2. Builder Pattern
- Configuration models built using Pydantic
- Hierarchical configuration structure

### 3. Connection Pooling
- Single Snowflake connection per action instance
- Lazy initialization of connection
- Proper cleanup in `close()` method

### 4. Batch Processing
- Configurable batch size for GraphQL queries
- Processes large glossaries efficiently
- Memory-efficient iteration

## Extension Points

### Add New Data Sources
Extend `_fetch_*` methods to support:
- Additional GraphQL entities
- REST API endpoints
- Custom data sources

### Add New Destinations
Create new destination classes similar to Snowflake:
- Databricks
- BigQuery
- PostgreSQL
- S3/Parquet files

### Add Event Processing
Modify `act()` method to:
- Listen for EntityChangeEvents
- Perform incremental updates
- Real-time synchronization

### Add Transformations
Extend `_transform_entity_to_row()` to:
- Include more metadata
- Calculate derived fields
- Apply business logic

## Testing Strategy

### Unit Tests
- Mock external dependencies (Snowflake, DataHub)
- Test individual methods
- Validate data transformations

### Integration Tests (Future)
- Test against real DataHub instance
- Test Snowflake connection
- End-to-end workflow validation

### Manual Testing
- Local execution with test config
- DataHub Cloud deployment
- Query validation in Snowflake

## Release Process

1. **Development**
   - Create feature branch
   - Make changes
   - Add tests
   - Update documentation

2. **Testing**
   - Run `pytest tests/`
   - Run `black action_glossary_export/`
   - Run `flake8 action_glossary_export/`
   - Manual testing

3. **Release**
   - Update version in `setup.py`
   - Create git tag: `git tag v0.2.0`
   - Push tag: `git push origin v0.2.0`
   - GitHub Actions automatically builds and releases

4. **Deployment**
   - Users pull latest from GitHub
   - Update Extra Pip Libraries in DataHub Cloud
   - Run ingestion source

## Best Practices

### Code Quality
- Type hints on all functions
- Comprehensive docstrings
- Consistent error handling
- Logging at appropriate levels

### Configuration
- Use environment variables for secrets
- Provide sensible defaults
- Validate configuration early

### Documentation
- Keep README up to date
- Provide working examples
- Document breaking changes
- Include troubleshooting guide

### Security
- Never commit credentials
- Use secrets management
- Validate inputs
- Sanitize SQL queries

## Future Enhancements

- [ ] Incremental updates (MERGE instead of truncate/insert)
- [ ] Event-driven updates (listen to EntityChangeEvents)
- [ ] Multi-destination support (BigQuery, Databricks)
- [ ] Relationship export (IsA, HasA)
- [ ] Asset-to-term association export
- [ ] Historical tracking (SCD Type 2)
- [ ] Metrics and monitoring
- [ ] Performance optimization for very large glossaries

---

**Project Status**: Production Ready ✅

**Maintainer**: Jonny Dixon

**Last Updated**: January 13, 2026
