import glob
import os
import sys
import xml.etree.ElementTree as ET
from ..TEDn import TEDn, TEDnResult
from ...symbolic.MxlFile import MxlFile


def scan_corpus(extended_flavor=True):
    mxl_files = glob.glob(
        "datasets/OpenScore-Lieder/scores/**/*.mxl",
        recursive=True
    )

    for path in mxl_files:
        print(path, "...")
        scan_mxl_file(path, extended_flavor)


def scan_mxl_file(path: str, extended_flavor: bool):
    mxl = MxlFile.load_mxl(path)

    for part in mxl.tree.findall("part"):
        # this runs fast! But a gold-to-gold runs crazy slow, one system takes 60s
        # and grows more than N^2, so do only system-wise comparison.
        result: TEDnResult = TEDn(
            ET.Element("part"), # empty tree
            part # to gold tree
        )
        print(result)
