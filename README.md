# vf-extractor
Python package designed for parsing information from Humphrey Visual Field (HVF) reports.

---

## Overview

`vf-extractor` is a **package-first Python project** that extracts structured information from Humphrey Visual Field reports. It includes:

- Core Python package (`vfextractor/`) with all parsing logic.
- Command-line interface (CLI) scripts.
- Optional **Streamlit app** (`app/`) for interactive usage.
- Documentation via **MkDocs** (`docs/`).

This layout allows easy integration into other Python projects while providing a user-friendly interface for non-developers.

---

## Features

- Parse HVF reports into structured data.
- CLI script for batch processing.
- Interactive Streamlit UI for uploading reports and visualizing results.
- Well-documented codebase with MkDocs support.
- Cross-platform support: Windows, macOS, Linux.

---

## Requirements

- Python 3.11+  
- pip

Optional dependencies for development:

- `streamlit`
- `mkdocs`
- `mkdocs-material`

All dependencies are included in `requirements.txt`.

---

## Installation

### macOS / Linux

```bash
# Clone the repository
git clone https://github.com/yourusername/vf-extractor.git
cd vf-extractor

# Install dependencies
./install.sh
