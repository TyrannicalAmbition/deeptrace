# DeepTrace · Test-log performance analyzer

[![TestPyPI Version](https://img.shields.io/badge/TestPyPI-v0.1.1-blue)](https://test.pypi.org/project/deeptrace/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**DeepTrace** is a powerful CLI tool and Python library designed to analyze and identify performance bottlenecks in automated test execution logs. It supports multiple formats including Playwright, Selenium, Allure, HAR files, and generic JSON logs.

## What Problems Does DeepTrace Solve?

### Current Challenges:
- **Slow Test Suites**: Identifying which specific steps are causing pipeline delays
- **Performance Regressions**: Detecting when tests become slower between releases  
- **Log Analysis Overhead**: Manual analysis of large test execution logs is time-consuming
- **Multi-Format Support**: Different testing tools generate different log formats
- **CI/CD Optimization**: Need for automated performance monitoring in pipelines

### DeepTrace Solutions:
- **Instant Performance Analysis**: Quickly pinpoint the slowest operations in your test logs
- **Multi-Format Support**: Works with Playwright, Selenium, Allure, HAR, and JSON logs out of the box
- **Regression Detection**: Compare test runs to identify performance degradations
- **Automated Reporting**: Generate markdown reports for CI artifacts and documentation
- **Rich Visual Output**: Beautiful console output with color coding and progress indicators

---

## Key Features

| ✔ | What it does                                                                                           |
|---|--------------------------------------------------------------------------------------------------------|
| ✅ | **Auto-detects log format** – just pass a file or directory, no `--format` flag needed                |
| ✅ | **Multiple format support** – Playwright, Selenium, Allure, HAR, and generic JSON                     |
| ✅ | **Performance threshold filtering** – show only steps slower than specified duration                    |
| ✅ | **Top-N analysis** – display the slowest N operations for quick identification                         |
| ✅ | **Rich console output** – color-coded, formatted display with ASCII-safe fallback                     |
| ✅ | **Markdown report generation** – perfect for CI artifacts and documentation                            |
| ✅ | **A/B comparison mode** – compare two test runs to spot performance regressions                       |
| ✅ | **Zero-config operation** – works out of the box with sensible defaults                               |
| ✅ | **Extensible parser API** – easily add support for new log formats                                    |

---

## Planned Features (Roadmap)

### 🔬 Advanced Analytics
- **Flaky Test Detection**: Identify tests with inconsistent execution times
- **Performance Trend Analysis**: Track performance changes over multiple runs
- **Bottleneck Categorization**: Classify slow operations by type (network, DOM, computation)

### Extended Format Support
- **Docker Log Analysis**: Parse and analyze container execution logs
- **Kubernetes Pod Logs**: Support for distributed test execution analysis
- **Custom Log Formats**: Enhanced plugin system for proprietary formats

### Enhanced Reporting
- **Interactive HTML Reports**: Rich visualizations with charts and graphs
- **Integration APIs**: Direct integration with popular CI/CD platforms
- **Performance Dashboards**: Real-time monitoring and alerting capabilities

### Enterprise Features
- **Premium Plugins**: Advanced features under `deeptrace.plugins` namespace
- **Team Collaboration**: Shared analysis and reporting features
- **Performance SLA Monitoring**: Automated alerts when thresholds are exceeded

---

## Installation

### From TestPyPI (Latest Development Version)
```bash
# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ deeptrace

# Or with pipx for isolated installation
pipx install -i https://test.pypi.org/simple/ deeptrace
```

### From PyPI (Stable Release - Coming Soon)
```bash
# Will be available soon on PyPI
pip install deeptrace
pipx install deeptrace
