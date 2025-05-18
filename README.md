# Slowpoke Finder

[![Build Status](https://img.shields.io/github/actions/workflow/status/TyrannicalAmbition/slowpocke-finder/ci.yml?branch=main)](https://github.com/TyrannicalAmbition/slowpocke-finder/actions)
[![PyPI Version](https://img.shields.io/pypi/v/slowpoke-finder)](https://pypi.org/project/slowpoke-finder/)
[![License](https://img.shields.io/github/license/TyrannicalAmbition/slowpocke-finder)](./LICENSE)

**Slowpoke Finder** is a CLI tool and Python library for analyzing automated test logs and finding the slowest steps in your test runs.  
It helps QA engineers, developers, and DevOps teams quickly identify which actions or steps in their Playwright, Selenium, or Allure-based test suites are bottlenecks, using log files or Allure results as input.

---

## Features

- **Universal Log Format Support**: Analyze logs from Playwright, Selenium (JSON/HAR), or Allure results folder.
- **Highlight Slow Steps**: Show the slowest steps (`--top N`) or all steps slower than a given threshold (`--threshold`).
- **Simple CLI**: Analyze logs with a single command.
- **Python API**: Use as a library in your automation scripts or test infrastructure.
- **Fast and Lightweight**: Designed to work with very large logs and fast parsing.

---

## Installation

Install via **pip** (or pipx for global CLI):

```bash
pip install slowpoke-finder