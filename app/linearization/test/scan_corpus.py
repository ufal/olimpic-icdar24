import glob
import os
import sys
from ..Linearizer import Linearizer
from ..Delinearizer import Delinearizer
from ...symbolic.MxlFile import MxlFile
from ...symbolic.split_part_to_systems import split_part_to_systems
from ...symbolic.Pruner import Pruner
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


def scan_mxl_file(path: str):
    pruner = Pruner(
        prune_durations=True, # TODO: this should be removed once I start to work on durations!
        prune_tremolo_marks=True, # patches a bug in the linearizer
    )

    mxl = MxlFile.load_mxl(path)
    for part in mxl.tree.findall("part"):
        linearizer = Linearizer() # errout=sys.stdout
        linearizer.process_part(part)

        text = " ".join(linearizer.output_tokens)
        # print(text)
        delinearizer = Delinearizer(errout=sys.stdout)
        delinearizer.process_text(text)
        # print(str(ET.tostring(delinearizer.part_element, "utf-8"), "utf-8"))

        pruner.process_part(part) # simplify gold before comparison
        pruner.process_part(delinearizer.part_element)
        compare_parts(
            expected=part,
            given=delinearizer.part_element
        )

        # pages = split_part_to_systems(part)
        # for page in pages:
        #     for system in page.systems:
        #         linearizer = Linearizer() # errout=sys.stdout
        #         linearizer.process_part(system.part)

        #         text = " ".join(linearizer.output_tokens)
        #         # print(text)
        #         delinearizer = Delinearizer(errout=sys.stdout)
        #         delinearizer.process_text(text)
        #         # print(str(ET.tostring(delinearizer.part_element, "utf-8"), "utf-8"))

        #         pruner.process_part(system.part) # simplify gold before comparison
        #         pruner.process_part(delinearizer.part_element)
        #         compare_parts(
        #             expected=system.part,
        #             given=delinearizer.part_element
        #         )


def compare_parts(expected: ET.Element, given: ET.Element):
    measures_e = expected.findall("measure")
    measures_g = given.findall("measure")
    assert len(measures_e) == len(measures_g)
    for i in range(len(measures_e)):
        compare_measures(measures_e[i], measures_g[i])


def compare_measures(expected: ET.Element, given: ET.Element):
    measure_number = expected.get("number")

    if len(expected) != len(given):
        print("Non-matching measure contents!")
        compare_elements(measure_number, expected, given)
        return

    # everything
    for e, g in zip(expected, given):
        compare_elements(measure_number, e, g)
    
    # pitch only
    # for e, g in zip(expected.iterfind("note"), given.iterfind("note")):
    #     e = e.find("pitch")
    #     g = g.find("pitch")
    #     if e is None or g is None:
    #         continue
    #     compare_elements(measure_number, e, g)


def compare_elements(measure_number: str, expected: ET.Element, given: ET.Element):
    e = ET.canonicalize(
        ET.tostring(expected),
        strip_text=True
    )
    g = ET.canonicalize(
        ET.tostring(given),
        strip_text=True
    )
    if e != g:
        print()
        print("MEASURE: ", measure_number)
        print("EXPECTED:", e)
        print("GIVEN:   ", g)
