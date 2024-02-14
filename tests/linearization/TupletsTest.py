from .LinearizerTestCase import LinearizerTestCase


class TupletsTest(LinearizerTestCase):
    def test_simple_2345(self):
        self.process_sample("tuplets/simple_2345")
    
    def test_simple_67(self):
        self.process_sample("tuplets/simple_67")
    
    def test_simple_89(self):
        self.process_sample("tuplets/simple_89")
