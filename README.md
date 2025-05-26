# Slowpoke Finder

[![Build Status](https://img.shields.io/github/actions/workflow/status/TyrannicalAmbition/slowpocke-finder/ci.yml?branch=main)](https://github.com/TyrannicalAmbition/slowpocke-finder/actions)
[![PyPI Version](https://img.shields.io/pypi/v/slowpoke-finder)](https://pypi.org/project/slowpoke-finder/)

**Slowpoke Finder** is a CLI tool and Python library for analyzing automated test logs and finding the slowest steps in
your test runs.  
It helps QA engineers, developers, and DevOps teams quickly identify which actions or steps in their Playwright,
Selenium, or Allure-based test suites are bottlenecks, using log files or Allure results as input.

---

## Features

- **Universal Log Format Support**: Analyze logs from Playwright, Selenium (JSON/HAR), or Allure results folder.
- **Highlight Slow Steps**: Show the slowest steps (`--top N`) or all steps slower than a given
  threshold (`--threshold`).
- **Deduplication**: Automatically merges steps with the same name to avoid duplicates in the output.
- **Advanced Statistics**: Shows median, mean, and custom percentiles (p50, p95, p99, etc.) with the `--percentiles` flag.
- **Markdown Report Generation**: Generate a Markdown report with `--report`.
- **Simple CLI**: Analyze logs with a single command.
- **Python API**: Use as a library in your automation scripts or test infrastructure.
- **Fast and Lightweight**: Designed to work with very large logs and fast parsing.

---

## Installation

### Currently, the library is published only on **Test PyPI**

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ slowpoke-finder
```

Install via **pip** (or pipx for global CLI):

```bash
pip install slowpoke-finder
```

---

## Usage

### CLI: Command-Line Examples

You must specify the input format using --format (or -f): `playwright`, `selenium`, or `allure`. The tool does not
auto-detect log format.

---

### Find Top N Slowest Steps

```bash
slowpoke-finder path/to/log.json --format playwright --top 5
```

The `--top` flag is optional and defaults to 5.
So you can simply run:

```bash
slowpoke-finder path/to/log.json --format playwright
```

---

### Find All Steps Above a Threshold

```bash
slowpoke-finder path/to/allure-results --format allure --threshold 1000
```

---

### Show Additional Percentiles

```bash
slowpoke-finder path/to/log.json --format playwright --percentiles 50 --percentiles 95 --percentiles 99
```

or short:
```bash
slowpoke-finder path/to/log.json -f playwright -p 50 -p 95 -p 99
```

---

### Analyze Selenium HAR Log

```bash
slowpoke-finder path/to/selenium.har --format selenium
```

---

### Generate a Markdown Report
Use the `--report` (or `-r`) flag to save results to a Markdown file.
Specify a directory name (it will be created if it does not exist); the report will be saved as report.md inside that directory.
```bash
slowpoke-finder path/to/log.json --format playwright --top 10 --report my-report-dir
```

---

## Common Arguments

`log`: Path to a log file or directory (e.g., JSON, HAR, or Allure results folder).

`--format` / `-f`: Input log format: playwright, selenium, allure.

`--top` / `-n`: Show top N the slowest steps (default: 5).

`--threshold` / `-t`: Show all steps slower than N ms (overrides --top if set).

`--report` / `-r`: Directory to save Markdown report (report will be report.md inside this directory).

`--percentiles` / `-p`: Additional percentiles for summary (repeatable flag).

---

## Python Library Usage

```python
from slowpoke_finder.registry import get
from slowpoke_finder.analyzer import top_slow_steps

parser = get("selenium")
steps = parser.parse("examples/selenium_actions.json")
top_steps = top_slow_steps(steps, top=3)

for step in top_steps:
    print(f"{step.name}: {step.duration} ms")
```

- Choose the parser by format: `get("selenium")`, `get("playwright")`, or `get("allure")`
- Each parser returns a list of Step objects (`.name`, `.start_ms`, `.end_ms`, `.duration`)

---

## Supported Formats

| Format         | Description                            | How to Use                                 |
|----------------|----------------------------------------|--------------------------------------------|
| **playwright** | Playwright JSON logs (`actions` array) | Point at a Playwright JSON log file        |
| **selenium**   | Selenium WebDriver logs (JSON or HAR)  | Point at a Selenium JSON/HAR log file      |
| **allure**     | Allure `allure-results` folder (JSON)  | Point at the root of an Allure results dir |
