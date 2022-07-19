"""
HazenTask.py
"""
from pydicom import dcmread


class HazenTask:

    def __init__(self, data_paths: list, report: bool = False, report_path: str = 'hazen_report'):
        self.data_paths = data_paths
        self.report: bool = report
        self.report_path: str = report_path
        self.data: list = self.read_data()

    def read_data(self) -> list:
        return [dcmread(dicom) for dicom in self.data_paths]

