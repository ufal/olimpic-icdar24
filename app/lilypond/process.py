import os
from svgelements import *
import xml.etree.ElementTree as ET


LILYPOND = "lilypond/bin/lilypond"
NOTEHEAD_PATH = "M218 136c55 0 108 -28 108 -89c0 -71 -55 -121 -102 -149c-35 -21 -75 -34 -116 -34c-55 0 -108 28 -108 89c0 71 55 121 102 149c35 21 75 34 116 34z"


def process(filename: str):
    outputfile = "app/lilypond/test"
    # os.system(f"{LILYPOND} --svg -o {outputfile} {filename}")

    SVGNS = "{http://www.w3.org/2000/svg}"

    tree = ET.parse(outputfile + ".svg")

    for i, g in enumerate(tree.getroot().iter(SVGNS + "g")):
        p = g.find(SVGNS + "path")
        if p is None:
            continue
        if p.attrib["transform"] != "scale(0.0040, -0.0040)":
            continue
        if p.attrib["d"] != NOTEHEAD_PATH:
            continue
        g.attrib["id"] = "notehead-" + str(i)
        p.attrib["fill"] = "#FF0000"

    tree.write(
        outputfile + "-modified.svg"
    )

    with open(outputfile + "-modified.svg", "r") as f:
        s: SVG = SVG.parse(f, reify=True)
        
        # for element in s.elements():
        #     print(element.values)
        #     print(type(element))

        # e: Group = s.get_element_by_id("g40")
        # print(e)
        # print([v for v in e.bbox()])

        # x1, y1, x2, y2 = e.bbox(with_stroke=True)
        # s.append(Rect(x1, y1, x2-x1, y2-y1, fill="#FF000055"))

        s.write_xml(outputfile + "-modified-2.svg")
