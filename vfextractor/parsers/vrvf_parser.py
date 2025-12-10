# vfextractor/parsers/vrvf_parser.py
from vfextractor.models import VFReport, PatientInfo, VFMatrix

class VRVFParser:
    def parse(self, text_data):
        # TODO: implement VRVF parsing logic
        patient = PatientInfo(name="Unknown", dob="", age=0, eye="OD", test_date="")
        matrix = VFMatrix(total_deviation=[], pattern_deviation=[])
        return VFReport(report_type="VRVF", patient_info=patient, matrix=matrix)
