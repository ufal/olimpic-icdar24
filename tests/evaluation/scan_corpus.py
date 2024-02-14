import glob
import os
import sys
import xml.etree.ElementTree as ET
from app.evaluation.TEDn import TEDn, TEDnResult
from app.symbolic.MxlFile import MxlFile


def scan_corpus():
    mxl_files = glob.glob(
        "datasets/OpenScore-Lieder/scores/**/*.mxl",
        recursive=True
    )
    mxl_files.sort()

    for path in mxl_files:
        print(path, "...")
        scan_mxl_file(path)


def scan_mxl_file(path: str):
    mxl = MxlFile.load_mxl(path)

    for part in mxl.tree.findall("part"):
        # this runs fast! But a gold-to-gold runs crazy slow, one system takes 60s
        # and grows more than N^2, so do only system-wise comparison.
        result: TEDnResult = TEDn(
            ET.Element("part"), # empty tree
            part # to gold tree
        )
        print(result)
