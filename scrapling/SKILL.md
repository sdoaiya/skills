---
name: scrapling
description: Use when installing, configuring, or writing code with the Scrapling Python package, including Fetcher, Selector, CLI usage, MCP server setup, browser-backed scraping, and HTML parsing tasks.
---

# Scrapling

Use this skill for tasks involving the `scrapling` Python package: fetching pages, parsing HTML, extracting text or attributes, and setting up the CLI or MCP server.

## When To Use

- Installing Scrapling in a new workspace
- Writing or fixing Python code that uses `Fetcher`, `DynamicFetcher`, `StealthyFetcher`, or `Selector`
- Running `scrapling` CLI commands
- Setting up browser dependencies with `scrapling install`
- Wiring Scrapling into Codex via the MCP server

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install "scrapling[all]"
.\.venv\Scripts\scrapling.exe install
.\.venv\Scripts\scrapling.exe --help
```

```python
from scrapling import Fetcher
from scrapling.parser import Selector

page = Fetcher.get("https://example.com")
print(page.status)
print(page.css("h1::text").get())

doc = Selector('<html><h1>Hello</h1><a href="/x">Link</a></html>')
print(doc.css("h1::text").get())
print(doc.css("a::attr(href)").get())
```

## Notes

- For the current package version, `Selector` is imported from `scrapling.parser`.
- Use `scrapling install` when browser dependencies are needed.
