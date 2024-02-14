import unittest
from app.linearization.Linearizer import Linearizer
from app.linearization.LmxFile import LmxFile
from app.symbolic.split_part_to_systems import split_part_to_systems
import os
import xml.etree.ElementTree as ET


class LinearizerTestCase(unittest.TestCase):
    def process_sample(self, sample_name: str, expected_errors=[]):
        samples_dir = os.path.join(os.path.dirname(__file__), "samples")
        xml_file_path = os.path.join(samples_dir, sample_name + ".xml")
        lmx_file_path = xml_file_path.replace(".xml", ".lmx")
        
        with open(xml_file_path) as file:
            tree = ET.parse(file)
        input_part = tree.find("part")
        input_pages = split_part_to_systems(input_part)
        assert len(input_pages) == 1
        input_systems = input_pages[0].systems

        lmx = LmxFile.load(lmx_file_path)

        self.assertEqual(
            len(lmx.systems),
            len(input_systems),
            "Expected a different number of systems"
        )

        for i in range(len(lmx.systems)):
            linearizer = Linearizer()
            linearizer.process_part(input_systems[i].part)

            errors = linearizer._errout.readlines()
            self.assertEqual(
                expected_errors,
                errors,
                "The linearization produced unexpected errors."
            )

            self.assertEqual(
                lmx.systems[i],
                linearizer.output_tokens,
                "Token sequences differ."
            )
