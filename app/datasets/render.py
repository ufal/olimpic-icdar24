import xml.etree.ElementTree as ET
from typing import Iterable, List, Optional, Tuple
import os
from ..symbolic.MxlFile import MxlFile


def prune_mxl_file(mxl: MxlFile):
    # remove the voice part completely
    id = mxl.resolve_piano_part_id()
    part_list = mxl.tree.find("part-list")
    score_part = mxl.tree.find(f"part-list/score-part[@id!='{id}']")
    part = mxl.tree.find(f"part[@id!='{id}']")
    part_list.remove(score_part)
    mxl.tree.getroot().remove(part)

    # remove work and identification
    work = mxl.tree.find("work")
    identification = mxl.tree.find("identification")
    mxl.tree.getroot().remove(work)
    mxl.tree.getroot().remove(identification)

    # remove credit text
    for credit in mxl.tree.findall("credit"):
        mxl.tree.getroot().remove(credit)

    # remove elements from the piano part
    measures = mxl.get_piano_part()
    to_remove: List[Tuple[ET.Element, ET.Element]] = []
    for measure in measures:
        for element in measure:
            pass

            # remove dynamics, crescendo, pedal, etc...
            # if element.tag == "direction":
            #     to_remove.append((measure, element))

            # remove positioning information
            if element.tag == "measure":
                del element.attrib["width"]

                for note in element:
                    if note.tag != "note":
                        continue
                    del note.attrib["default-x"]
                    del note.attrib["default-y"]

                    # remove notations
                    # NOTATIONS_TO_REMOVE = [
                    #     "..."
                    # ]
                    # notations = note.find("notations")
                    # for notation in notations or []:
                    #     if notation.tag in NOTATIONS_TO_REMOVE:
                    #         notations.remove(notation)

    for p, e in to_remove:
        p.remove(e)


def append_mxl_file(mxl: MxlFile, mxl_extension: MxlFile):
    piano_part = mxl.get_piano_part()
    extension = mxl_extension.get_piano_part()

    empty_measure = ET.Element("measure")
    empty_print = ET.Element("print", {"new-page": "yes"})
    empty_measure.append(empty_print)
    empty_note = ET.Element("note")
    empty_note_type = ET.Element("type")
    empty_note_type.text = "quarter"
    empty_note.append(empty_note_type)
    empty_note_lyric = ET.Element("lyric")
    empty_note_lyric_text = ET.Element("text")
    empty_note_lyric_text.text = "ThisIsFileSeparatorPage"
    empty_note_lyric.append(empty_note_lyric_text)
    empty_note.append(empty_note_lyric)
    empty_measure.append(empty_note)
    piano_part.append(empty_measure)

    first_measure = extension.find("measure")
    first_print = first_measure.find("print")
    first_print.attrib["new-page"] = "yes"

    for measure in extension:
        piano_part.append(measure)


LILYPOND = "lilypond/bin/lilypond"
MUSICXML2LY = "lilypond/bin/musicxml2ly"
MUSESCORE = "musescore/musescore.AppImage"
TMP_FILE = "app/datasets/render"


mxl = MxlFile.load(
    "Chaminade,_Cécile/_/Alleluia",
    "6260992"
)
prune_mxl_file(mxl)

mxl_extension = MxlFile.load(
    "Chaminade,_Cécile/_/Amertume",
    "6261036"
)
prune_mxl_file(mxl_extension)

append_mxl_file(mxl, mxl_extension)

# filenames
xml_file = TMP_FILE + ".xml"
ly_file = TMP_FILE + ".ly"
pdf_file = TMP_FILE + ".pdf"
svg_file = TMP_FILE + ".svg"

# store the temp file
mxl.tree.write(xml_file)

# # convert to lilypond
# e = os.system(f"{MUSICXML2LY} --absolute -o {ly_file} {xml_file}")
# assert e == 0
# # render to PDF
# e = os.system(f"{LILYPOND} -o {pdf_file} {ly_file}")
# assert e == 0
# LILYPOND SUCKS! IT MESSES UP ACCIDENTALS AND ORIENTATION OF THINGS.
# I'LL RATHER USE MUSESCORE WITH MERGED FILES FOR SPEED THAN LILYPOND!

# render to PDF
# e = os.system(f"{MUSESCORE} {xml_file} -o {pdf_file}")
# assert e == 0

# render to SVG
e = os.system(f"{MUSESCORE} {xml_file} -o {svg_file}")
assert e == 0
