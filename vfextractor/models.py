# vfextractor/models.py
from dataclasses import dataclass
from typing import List

@dataclass
class PatientInfo:
    name: str
    dob: str
    age: int
    eye: str
    test_date: str

@dataclass
class VFMatrix:
    total_deviation: List[float]
    pattern_deviation: List[float]

@dataclass
class VFReport:
    report_type: str               # 'HVF' or 'VRVF'
    patient_info: PatientInfo
    matrix: VFMatrix
    reliability_indices: dict = None   # Optional: Fixation Loss, FP, FN
    global_indices: dict = None        # Optional: MD, PSD, VFI
