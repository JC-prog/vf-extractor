# Distributing vf-extractor (Offline / Air-Gapped)

This guide explains how to build and distribute a fully portable version of vf-extractor
that runs on Windows PCs with no internet connection and no software installation required.

## How it works

The portable build packages:
- A self-contained Python 3.12 runtime (official embeddable distribution — no installer)
- All Python dependencies pre-installed
- PaddleOCR models pre-downloaded (no internet needed at runtime)
- The application source

Users receive a single folder (~1.4 GB) and launch the app by double-clicking `run.bat`.
No admin rights, no installation, no internet.

---

## For developers: building the portable package

> Run these steps on an **internet-connected** machine.

### Prerequisites
- Python 3.12 installed and on PATH
- Project dependencies installed (`install.bat`)
- `curl` available (included in Windows 10/11)

### Step 1 — Download OCR models

Run once to populate the `models/` directory:

```batch
python scripts\download_models.py
```

This downloads PaddleOCR's English OCR models (~300 MB) into `models/`.
The script may take several minutes. A test prediction is run at the end to confirm success.

### Step 2 — Build the portable folder

```batch
scripts\build_portable.bat
```

This will:
1. Download Python 3.12.10 embeddable runtime
2. Install all packages from `requirements.txt` into the embedded Python
3. Install the `vfextractor` package from local source
4. Copy `app/`, `vfextractor/`, `models/`, and `.streamlit/` into `dist/`
5. Write the `dist\run.bat` launcher

Output: `dist\` folder (~1.4 GB total).

---

## For IT / distribution

Copy the entire `dist\` folder to the target machine via USB drive or shared network folder.

The folder is self-contained — no files outside it are required.

```
dist\
├── python\          ← Embedded Python 3.12 runtime
├── app\             ← Streamlit web application
├── vfextractor\     ← Core extraction package
├── models\          ← Pre-downloaded PaddleOCR models
├── .streamlit\      ← Streamlit config (telemetry disabled)
└── run.bat          ← Launcher — users double-click this
```

---

## For end users

1. Copy the `dist\` folder to your PC (e.g. `C:\vf-extractor\`)
2. Double-click **`run.bat`**
3. A browser window opens automatically at `http://localhost:8501`
4. Upload HVF or VRVF report files and click **Run Pipeline**

> The app runs entirely on your local machine. No data is sent to the internet.

---

## Troubleshooting

**Browser does not open automatically**
Open your browser manually and go to `http://localhost:8501`

**`run.bat` closes immediately**
Right-click `run.bat` → Open with → Notepad to check for errors,
or run it from Command Prompt to see the full output.

**Extraction gives wrong results**
Ensure the correct template is selected (HVF or VRVF) and the image is
a clear scan at 300 DPI or higher.

---

## Re-building after a code update

After pulling new code changes on the dev machine, re-run both steps:

```batch
python scripts\download_models.py   # only needed if models changed
scripts\build_portable.bat
```

The `models\` directory is preserved between builds unless you delete it.
