"""
HazenTask.py
"""
from pydicom import dcmread


class HazenTask(object):

    def __init__(self, data_paths: list, report: bool = False, report_path: str = 'report.txt'):
        self.data_paths = data_paths
        self.report: bool = report
        self.report_path: str = report_path
        self.data: list = self.read_data()

    def read_data(self) -> list:
        return [dcmread(dicom) for dicom in self.data_paths]

