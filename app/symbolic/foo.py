import glob
from app.linearization.Linearizer import Linearizer
from app.symbolic.MxlFile import MxlFile
from app.symbolic.split_part_to_systems import split_part_to_systems
from app.symbolic.part_to_score import part_to_score
import xml.etree.ElementTree as ET


mxl_files = list(sorted(
    glob.glob("datasets/OpenScore-Lieder/scores/**/*.mxl", recursive=True)
))


for mxl_path in mxl_files:
    print(mxl_path, "...")
    mxl_file = MxlFile.load_mxl(mxl_path)
    
    for part in mxl_file.tree.getroot().findall("part"):

        # split the xml
        pages = split_part_to_systems(part)

        # check all pages and systems match system-wise linearization
        for pi, page in enumerate(pages):
            for si, system in enumerate(page.systems):
                # system_linearizer = Linearizer()
                # system_linearizer.process_part(system.part)
                # system_tokens = system_linearizer.output_tokens

                print()
                score = part_to_score(system.part)
                xml_string = str(ET.tostring(
                    score.getroot(),
                    encoding="utf-8",
                    xml_declaration=True
                ), "utf-8")
                print(xml_string)

    break
