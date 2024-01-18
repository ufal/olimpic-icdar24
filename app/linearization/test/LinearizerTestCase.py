import unittest
from ..Linearizer import Linearizer
from ..LmxFile import LmxFile
import os
import xml.etree.ElementTree as ET


class LinearizerTestCase(unittest.TestCase):
    def setUp(self):
        self.linearizer = Linearizer()
    
    def process_sample(self, sample_name: str, expected_errors=[]):
        samples_dir = os.path.join(os.path.dirname(__file__), "samples")
        xml_file_path = os.path.join(samples_dir, sample_name + ".xml")
        lmx_file_path = xml_file_path.replace(".xml", ".lmx")
        
        with open(xml_file_path) as file:
            tree = ET.parse(file)
        part = tree.find("part")

        lmx = LmxFile.load(lmx_file_path)

        self.linearizer.process_part(part)

        errors = self.linearizer._errout.readlines()
        self.assertEqual(
            expected_errors,
            errors,
            "The linearization produced unexpected errors."
        )

        self.assertEqual(
            1,
            len(self.linearizer.output_tokens),
            "More than one page of music has been created"
        )

        systems = self.linearizer.output_tokens[0]
        self.assertEqual(
            len(lmx.systems),
            len(systems),
            "Expected a different number of systems"
        )

        for i in range(len(lmx.systems)):
            self.assertEqual(
                lmx.systems[i],
                systems[i],
                "Token sequences differ."
            )
