import os
from typing import Dict, Any
from .config import LIEDER_CORPUS_PATH
from ..symbolic.MxlFile import MxlFile
from ..linearization.Linearizer import Linearizer
from ..symbolic.split_part_to_systems import split_part_to_systems
from ..symbolic.part_to_score import part_to_score
import xml.etree.ElementTree as ET


def prepare_corpus_lmx_and_musicxml(
    scores: Dict[int, Dict[str, Any]],
    soft=False
):
    for score_id, score in scores.items():
        score_folder = os.path.join(LIEDER_CORPUS_PATH, "scores", score["path"])
        mxl_path = os.path.join(score_folder, f"lc{score_id}.mxl")

        musicxml_folder = os.path.join(score_folder, "musicxml")
        lmx_folder = os.path.join(score_folder, "lmx")

        # skip already converted
        if soft:
            if os.path.isdir(musicxml_folder) and os.path.isdir(lmx_folder):
                continue

        os.makedirs(musicxml_folder, exist_ok=True)
        os.makedirs(lmx_folder, exist_ok=True)

        print("Preparing LMX and MusicXML:", score_folder, "...")
        
        mxl = MxlFile.load_mxl(mxl_path)
        part = mxl.get_piano_part()
        pages = split_part_to_systems(part)

        for pi, page in enumerate(pages):
            for si, system in enumerate(page.systems):
                page_number = str(pi + 1)
                system_number = str(si + 1)

                # write the system musicxml
                musicxml_path = os.path.join(
                    musicxml_folder, f"p{page_number}-s{system_number}.musicxml"
                )
                system_score = part_to_score(system.part)
                xml_string = str(ET.tostring(
                    system_score.getroot(),
                    encoding="utf-8",
                    xml_declaration=True
                ), "utf-8")
                with open(musicxml_path, "w") as file:
                    file.write(xml_string + "\n")

                # linearize
                linearizer = Linearizer()
                linearizer.process_part(system.part)

                # write LMX
                lmx_path = os.path.join(
                    lmx_folder, f"p{page_number}-s{system_number}.lmx"
                )
                lmx_string = " ".join(linearizer.output_tokens)
                with open(lmx_path, "w") as file:
                    file.write(lmx_string + "\n")
