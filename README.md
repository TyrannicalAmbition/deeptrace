# DeepTrace · Test-log performance analyzer

[![Build Status](https://img.shields.io/github/actions/workflow/status/TyrannicalAmbition/deeptrace/ci.yml?branch=main)](https://github.com/TyrannicalAmbition/deeptrace/actions)
[![PyPI Version](https://img.shields.io/pypi/v/deeptrace)](https://pypi.org/project/deeptrace/)

**DeepTrace** is a tiny CLI + Python library that pinpoints the slowest steps inside automated-test logs  
(Playwright, Selenium, Allure, and more).  
Perfect for QA engineers, SDETs and DevOps when every second in the pipeline counts.

---

## Key features

| ✔ | What it does                                                                                           |
|---|--------------------------------------------------------------------------------------------------------|
| ✅ | **Auto-detects log format** – just pass a file or an `allure-results` directory, no `--format` needed. |
| ✅ | Works with **JSON**, **HAR**, and **Allure** out of the box; new parsers plug-in via a simple API.     |
| ✅ | CLI shows the *top N* slowest steps or everything slower than a threshold.                             |
| ✅ | Rich-styled **colour output** with ASCII-safe fallback.                                                |
| ✅ | Generates **Markdown reports** (`--report` flag) for CI artefacts.                                     |
| ✅ | **A/B comparison** (`compare`) to spot regressions between two runs.                                   |
| ✅ | MIT-licensed, pure-Python, zero non-std deps except `rich` and `typer`.                                |

> **Coming soon** – paid plug-ins (e.g. *flaky-test detector*).  
> The core stays FOSS; premium modules will live under the `deeptrace.plugins` namespace and require a licence key.

---

## Installation

```bash
pip install deeptrace              # from PyPI
# or
pipx install deeptrace             # isolates the CLI in its own venv
