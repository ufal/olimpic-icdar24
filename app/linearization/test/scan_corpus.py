import glob
import os
import sys
from ..Linearizer import Linearizer
from ..Delinearizer import Delinearizer
from ...symbolic.MxlFile import MxlFile
from ...symbolic.split_part_to_systems import split_part_to_systems
import xml.etree.ElementTree as ET


def scan_corpus():
    mxl_files = glob.glob(
        "datasets/OpenScore-Lieder/scores/**/*.mxl",
        recursive=True
    )
    mxl_files.sort()

    for path in mxl_files:
        print(path, "...")
        scan_mxl_file(path)
        # break


def scan_mxl_file(path: str):
    mxl = MxlFile.load_mxl(path)
    for part in mxl.tree.findall("part"):
        pages = split_part_to_systems(part)
        for page in pages:
            for system in page.systems:
                linearizer = Linearizer() # errout=sys.stdout
                linearizer.process_part(system.part)

                text = " ".join(linearizer.output_tokens)
                # print(text)
                delinearizer = Delinearizer(errout=sys.stdout)
                delinearizer.process_text(text)
                # print(str(ET.tostring(delinearizer.part_element, "utf-8"), "utf-8"))
