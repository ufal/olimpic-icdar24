import os
import sys
import yaml
from app.datasets.synthetic_01.config import *
from app.symbolic.MxlFile import MxlFile
import xml.etree.ElementTree as ET
from collections import Counter


IGNORE_SCORES = [
    5840072,
    5060972,

    # have weird time signatures which create weird tuplets
    # 6416048,
    # 5639135,
]


with open(os.path.join(LIEDER_CORPUS_PATH, "data/scores.yaml")) as f:
    corpus_scores = yaml.load(f, Loader=yaml.FullLoader)

keys = Counter()

for score_id in corpus_scores.keys():
    mxl_path = os.path.join(DATASET_PATH, "mxl", f"{score_id}.mxl")
    print(mxl_path)
    if score_id in IGNORE_SCORES:
        print("SKIPPING DUE TO IGNORE")
        continue
    try:
        mxl = MxlFile.load_mxl(mxl_path)
    except Exception as e:
        print("Failed to load:", score_id)
        continue
    part = mxl.get_piano_part()

    from app.linearization.Linearizer import Linearizer
    l = Linearizer(errout=sys.stdout)
    l.process_part(part)

    continue
    for measure in part:
        for note in measure:
            if note.tag == "note":
                notations = note.find("notations")
                if notations is not None:
                    tuplet = notations.find("tuplet")
                    if tuplet is not None and len(tuplet) > 0:
                        print(ET.tostring(tuplet, "utf-8"))
                        keys.update({ET.tostring(tuplet, "utf-8"): 1})
                    # print(ET.tostring(notations, "utf-8"))
                    # keys.update({key_token: 1})
                # print(ET.tostring(note, "utf-8"))

        #     for notation in note.find("notations") or []:
        #         if notation.tag == "tied" and notation.attrib.get("type") not in ["start", "stop"]:
        #             print(ET.tostring(notation, "utf-8"))

print(keys)