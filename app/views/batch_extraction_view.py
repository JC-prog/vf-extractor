import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
APP_DIR = CURRENT_DIR.parent

CONFIG_DIR = APP_DIR / "config"
TEMPLATE_DIR = CONFIG_DIR / "templates"
DATA_DIR = APP_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

HVF_TEMPLATE_PATH = TEMPLATE_DIR / "hvf.json"
VRVF_TEMPLATE_PATH = TEMPLATE_DIR / "vrvf.json"

TEMPLATE_MAP = {
    "HVF": HVF_TEMPLATE_PATH,
    "VRVF": VRVF_TEMPLATE_PATH,
}

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

try:
    PROJECT_ROOT = APP_DIR.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from vfextractor.pipeline.pipeline import cropped_pipeline
    from vfextractor.preprocessing.converter import convert_from_path

except ModuleNotFoundError as e:
    st.error(
        f"Error loading module: {e}. Ensure 'vfextractor' is installed or the "
        f"project root is correctly added to system path: {PROJECT_ROOT}"
    )


def _get_eye_side(filename: str) -> str | None:
    """Returns 'left' or 'right' from _OS / _OD in the filename, or None if ambiguous."""
    stem = Path(filename).stem.upper()
    has_os = "_OS" in stem
    has_od = "_OD" in stem
    if has_os and not has_od:
        return "left"
    if has_od and not has_os:
        return "right"
    return None


def _scan_input_dir() -> dict[str, list[Path]]:
    """Returns {patient_name: [file_path, ...]} for all patient subdirs in INPUT_DIR."""
    patients: dict[str, list[Path]] = {}
    if not INPUT_DIR.exists():
        return patients
    for patient_dir in sorted(INPUT_DIR.iterdir()):
        if not patient_dir.is_dir():
            continue
        files = [
            f
            for f in sorted(patient_dir.iterdir())
            if f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        if files:
            patients[patient_dir.name] = files
    return patients


def batch_extraction_view():
    st.title("Batch Extraction")

    st.caption(
        f"Place patient folders inside `{INPUT_DIR.relative_to(APP_DIR.parent)}`."
        " Each file must contain `_OS` (left eye) or `_OD` (right eye) in its name."
    )

    # --- Template selection ---
    template_selection = st.selectbox("Select Template", list(TEMPLATE_MAP.keys()))
    base_template_path = TEMPLATE_MAP[template_selection]

    # --- Scan input directory ---
    if not INPUT_DIR.exists():
        st.warning(
            f"Input directory not found: `{INPUT_DIR}`\n\n"
            "Create it and add patient subfolders:\n"
            "```\n"
            "data/input/\n"
            "  PatientName/\n"
            "    1_OS.pdf\n"
            "    2_OD.pdf\n"
            "```"
        )
        return

    patients = _scan_input_dir()

    if not patients:
        st.info(
            "No patient folders with supported files found in the input directory.\n\n"
            "Expected structure:\n"
            "```\n"
            "data/input/\n"
            "  PatientName/\n"
            "    1_OS.pdf\n"
            "    2_OD.pdf\n"
            "```"
        )
        return

    # --- Preview detected files ---
    total_files = sum(len(files) for files in patients.values())
    with st.expander(
        f"Detected {len(patients)} patient(s), {total_files} file(s)", expanded=True
    ):
        for name, files in patients.items():
            lines = []
            for f in files:
                eye = _get_eye_side(f.name)
                if eye == "left":
                    label = "OS"
                elif eye == "right":
                    label = "OD"
                else:
                    label = "? (skipped — no _OS/_OD)"
                lines.append(f"- {f.name} &nbsp; `{label}`")
            st.markdown(f"**{name}**  \n" + "  \n".join(lines))

    # --- Run button ---
    run_button = st.button("Run Batch Extraction", type="primary")

    if not run_button:
        return

    all_rows: list[dict] = []
    errors: list[str] = []

    progress = st.progress(0)
    status = st.empty()
    processed = 0

    for patient_name, files in patients.items():
        for file_path in files:
            eye_side = _get_eye_side(file_path.name)

            if eye_side is None:
                errors.append(
                    f"{patient_name}/{file_path.name}: skipped — "
                    "filename must contain `_OS` or `_OD`"
                )
                processed += 1
                progress.progress(processed / total_files)
                continue

            template_path = base_template_path.with_stem(
                base_template_path.stem + f"_{eye_side}"
            )
            eye_label = "OS" if eye_side == "left" else "OD"

            status.text(f"Processing {patient_name} — {file_path.name} ({eye_label})…")

            temp_files: list[str] = []
            images_to_process: list[str] = []

            try:
                if file_path.suffix.lower() == ".pdf":
                    pages = convert_from_path(str(file_path))
                    for img in pages:
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".png"
                        ) as tmp:
                            img.save(tmp.name, "PNG")
                            images_to_process.append(tmp.name)
                            temp_files.append(tmp.name)
                else:
                    images_to_process.append(str(file_path))

                for img_path in images_to_process:
                    data = cropped_pipeline(img_path, template_path, output_dir=None)
                    row = {
                        "patient": patient_name,
                        "eye": eye_label,
                        "file": file_path.name,
                        **data,
                    }
                    all_rows.append(row)

            except Exception as e:
                errors.append(f"{patient_name}/{file_path.name}: {e}")

            finally:
                for tmp in temp_files:
                    try:
                        os.unlink(tmp)
                    except OSError:
                        pass

            processed += 1
            progress.progress(processed / total_files)

    status.empty()
    progress.empty()

    # --- Errors ---
    if errors:
        with st.expander(f"{len(errors)} file(s) skipped or failed"):
            for err in errors:
                st.warning(err)

    # --- Results ---
    if not all_rows:
        st.error("No data was extracted. Check that the template matches your files.")
        return

    df = pd.DataFrame(all_rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUTPUT_DIR / f"batch_{timestamp}.csv"
    df.to_csv(csv_path, index=False)

    st.success(
        f"Extracted {len(all_rows)} record(s) from {len(patients)} patient(s). "
        f"Saved to `{csv_path.relative_to(APP_DIR.parent)}`."
    )

    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name=f"batch_{timestamp}.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    with st.expander("Preview"):
        st.dataframe(df, use_container_width=True)
