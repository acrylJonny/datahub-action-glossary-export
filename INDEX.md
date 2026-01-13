# Documentation Index

Welcome! This index helps you navigate the complete documentation for the DataHub Glossary Export Action.

---

## 🚀 Getting Started

Start here if you're new to the project:

1. **[OVERVIEW.md](OVERVIEW.md)** ⭐ **START HERE**
   - Complete project summary
   - What's included
   - Quick links to all resources

2. **[QUICKSTART.md](QUICKSTART.md)** ⚡ **5-Minute Setup**
   - Fastest path to running the action
   - Local or DataHub Cloud
   - Basic queries to try

3. **[README.md](README.md)** 📖 **Main Documentation**
   - Complete user guide
   - All features explained
   - Configuration reference
   - Troubleshooting

---

## 🎯 For Your Role

### 👨‍💼 Business Users / Analysts

**Goal**: Export glossary and analyze the data

1. Start: [QUICKSTART.md](QUICKSTART.md)
2. Then: [example_queries.sql](example_queries.sql) - 30+ pre-built queries
3. Reference: [README.md](README.md) - Understanding the data model

**What you'll learn**:
- How to export your glossary to Snowflake
- What data gets exported
- How to query and analyze the data

### 👨‍💻 Data Engineers / DevOps

**Goal**: Deploy and maintain the action in production

1. Start: [DEPLOYMENT.md](DEPLOYMENT.md) - Step-by-step DataHub Cloud deployment
2. Reference: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Technical architecture
3. Troubleshoot: [README.md](README.md#troubleshooting)

**What you'll learn**:
- How to deploy to DataHub Cloud
- How to manage secrets and configuration
- How to monitor and troubleshoot
- How to schedule regular exports

### 👨‍🔬 Developers / Contributors

**Goal**: Understand the codebase and extend functionality

1. Start: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Architecture overview
2. Then: Review `action_glossary_export/glossary_export_action.py`
3. Tests: `tests/test_glossary_export_action.py`
4. Reference: [SUMMARY.md](SUMMARY.md) - Design patterns and extension points

**What you'll learn**:
- How the action works internally
- How to extend and customize
- How to add tests
- How to contribute

---

## 📚 Complete Documentation

### Core Documentation

| File | Lines | Purpose |
|------|-------|---------|
| **[OVERVIEW.md](OVERVIEW.md)** | 340 | Complete project summary, quick reference |
| **[README.md](README.md)** | 379 | Main user documentation |
| **[QUICKSTART.md](QUICKSTART.md)** | 147 | Fast-track setup guide |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | 283 | DataHub Cloud deployment guide |
| **[SUMMARY.md](SUMMARY.md)** | 408 | Comprehensive project overview |
| **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** | 315 | Technical architecture and code structure |

### Code & Configuration

| File | Lines | Purpose |
|------|-------|---------|
| **[action_glossary_export/glossary_export_action.py](action_glossary_export/glossary_export_action.py)** | 585 | Main action implementation |
| **[action_glossary_export/__init__.py](action_glossary_export/__init__.py)** | 18 | Package initialization |
| **[setup.py](setup.py)** | 55 | Package installation configuration |
| **[example_action.yaml](example_action.yaml)** | 31 | Configuration example |
| **[requirements.txt](requirements.txt)** | 17 | Dependencies |

### Testing

| File | Lines | Purpose |
|------|-------|---------|
| **[tests/test_glossary_export_action.py](tests/test_glossary_export_action.py)** | 293 | Unit tests |
| **[.github/workflows/test.yml](.github/workflows/test.yml)** | 45 | CI pipeline |
| **[.github/workflows/release.yml](.github/workflows/release.yml)** | 37 | Release automation |

### Examples & Queries

| File | Lines | Purpose |
|------|-------|---------|
| **[example_queries.sql](example_queries.sql)** | 392 | 30+ SQL query examples |

---

## 🗂️ By Topic

### Installation & Setup

- **Local Installation**: [QUICKSTART.md](QUICKSTART.md#option-a-local-testing-fastest)
- **DataHub Cloud**: [QUICKSTART.md](QUICKSTART.md#option-b-datahub-cloud-production) or [DEPLOYMENT.md](DEPLOYMENT.md)
- **Dependencies**: [requirements.txt](requirements.txt)
- **Configuration**: [README.md](README.md#configuration)

### Configuration

- **All Options**: [README.md](README.md#configuration-parameters)
- **Example File**: [example_action.yaml](example_action.yaml)
- **Environment Variables**: [README.md](README.md#configuration)
- **Snowflake Setup**: [README.md](README.md#snowflake-configuration)

### Usage

- **Running Locally**: [QUICKSTART.md](QUICKSTART.md#option-a-local-testing-fastest)
- **Running in DataHub Cloud**: [DEPLOYMENT.md](DEPLOYMENT.md#step-3-create-a-new-ingestion-source)
- **Scheduling**: [DEPLOYMENT.md](DEPLOYMENT.md#running-on-a-schedule)
- **Manual Execution**: [DEPLOYMENT.md](DEPLOYMENT.md#manual-execution)

### Data & Queries

- **Output Schema**: [README.md](README.md#output-table-schema)
- **Example Data**: [OVERVIEW.md](OVERVIEW.md#example-data)
- **Basic Queries**: [example_queries.sql](example_queries.sql)
- **Reporting Queries**: [example_queries.sql](example_queries.sql) (Data Quality, Dashboards)

### Troubleshooting

- **Common Issues**: [README.md](README.md#troubleshooting)
- **DataHub Cloud Issues**: [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)
- **Quick Fixes**: [QUICKSTART.md](QUICKSTART.md#troubleshooting)

### Development

- **Architecture**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Code Structure**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#directory-tree)
- **Design Patterns**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#design-patterns)
- **Testing**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#testing-strategy)
- **Extension Points**: [SUMMARY.md](SUMMARY.md#customization-ideas)

### Advanced Topics

- **Performance**: [OVERVIEW.md](OVERVIEW.md#performance)
- **Security**: [OVERVIEW.md](OVERVIEW.md#security)
- **Customization**: [SUMMARY.md](SUMMARY.md#customization-ideas)
- **Private Repos**: [DEPLOYMENT.md](DEPLOYMENT.md#using-private-github-repository)

---

## 🔍 Search Guide

### I want to...

**Install and run the action locally**
→ [QUICKSTART.md](QUICKSTART.md#option-a-local-testing-fastest)

**Deploy to DataHub Cloud**
→ [DEPLOYMENT.md](DEPLOYMENT.md)

**Understand the output table**
→ [README.md](README.md#output-table-schema)

**See example queries**
→ [example_queries.sql](example_queries.sql)

**Understand how it works**
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**Troubleshoot an issue**
→ [README.md](README.md#troubleshooting)

**Configure Snowflake settings**
→ [README.md](README.md#snowflake-configuration)

**Schedule regular exports**
→ [DEPLOYMENT.md](DEPLOYMENT.md#running-on-a-schedule)

**Customize the action**
→ [SUMMARY.md](SUMMARY.md#customization-ideas)

**Run the tests**
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#testing-strategy)

**Contribute to the project**
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#release-process)

---

## 📊 File Statistics

| Category | Files | Lines |
|----------|-------|-------|
| Documentation | 7 | 2,272 |
| Code | 2 | 603 |
| Tests | 1 | 293 |
| Config | 4 | 103 |
| SQL Examples | 1 | 392 |
| CI/CD | 2 | 82 |
| **Total** | **17** | **3,745** |

---

## 🎓 Learning Paths

### Path 1: Quick Evaluation (15 minutes)

1. Read [OVERVIEW.md](OVERVIEW.md) (5 min)
2. Skim [QUICKSTART.md](QUICKSTART.md) (5 min)
3. Browse [example_queries.sql](example_queries.sql) (5 min)

**Outcome**: Understand what the action does and decide if it's useful

### Path 2: First Deployment (30 minutes)

1. Follow [QUICKSTART.md](QUICKSTART.md) for local testing (10 min)
2. Verify in Snowflake (5 min)
3. Try queries from [example_queries.sql](example_queries.sql) (15 min)

**Outcome**: Working local installation with data in Snowflake

### Path 3: Production Deployment (1 hour)

1. Follow [DEPLOYMENT.md](DEPLOYMENT.md) completely (30 min)
2. Set up secrets and configuration (15 min)
3. Test and verify (15 min)

**Outcome**: Production-ready deployment in DataHub Cloud

### Path 4: Deep Understanding (2 hours)

1. Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) (30 min)
2. Review code in `action_glossary_export/` (45 min)
3. Run tests locally (15 min)
4. Read [SUMMARY.md](SUMMARY.md) (30 min)

**Outcome**: Full understanding of architecture and implementation

---

## 🆘 Getting Help

### Self-Service Resources

1. **Check this index** - Find the right documentation
2. **Search documentation** - Use Cmd/Ctrl+F
3. **Try example queries** - Most questions answered in [example_queries.sql](example_queries.sql)
4. **Review troubleshooting** - Common issues in [README.md](README.md#troubleshooting)

### Community Support

- 💬 **DataHub Slack**: Join the community
- 🐛 **GitHub Issues**: Report bugs or ask questions
- 📧 **Email**: Contact Brock Griffey
- 📖 **DataHub Docs**: https://datahubproject.io/docs/actions

---

## 📝 Documentation Quality

All documentation includes:

- ✅ Clear step-by-step instructions
- ✅ Working code examples
- ✅ Troubleshooting sections
- ✅ Links to related resources
- ✅ Author and date information
- ✅ Table of contents (where appropriate)

---

## 🔄 Documentation Updates

**Last Updated**: January 13, 2026  
**Version**: 0.1.0  
**Maintainer**: Brock Griffey

To suggest improvements:
1. Open a GitHub issue
2. Submit a pull request
3. Contact the maintainer

---

## ⭐ Most Important Files

If you only read 3 files, make them these:

1. **[OVERVIEW.md](OVERVIEW.md)** - Complete summary
2. **[QUICKSTART.md](QUICKSTART.md)** - Get started fast
3. **[example_queries.sql](example_queries.sql)** - See what's possible

---

**Happy exploring!** 🚀

Need help? Start with the appropriate section above or check [OVERVIEW.md](OVERVIEW.md).
