from .LinearizerTestCase import LinearizerTestCase


class BasicsTest(LinearizerTestCase):
    def test_one_empty_measure(self):
        self.process_sample("basics/one_empty_measure")
    
    def test_note_types(self):
        self.process_sample("basics/note_types")
    
    def test_grandstaff(self):
        self.process_sample("basics/grandstaff")
