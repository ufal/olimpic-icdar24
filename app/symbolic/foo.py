import glob
from app.linearization.Linearizer import Linearizer
from app.symbolic.MxlFile import MxlFile
from app.symbolic.split_part_to_systems import split_part_to_systems
import xml.etree.ElementTree as ET


mxl_files = list(sorted(
    glob.glob("datasets/OpenScore-Lieder/scores/**/*.mxl", recursive=True)
))


# start_from = "datasets/OpenScore-Lieder/scores/Brahms,_Johannes/7_Lieder,_Op.48/5_Trost_in_Tränen/lc5071629.mxl"
# i = mxl_files.index(start_from)
# mxl_files = mxl_files[i:i+1]


for mxl_path in mxl_files:
    print(mxl_path, "...")
    mxl_file = MxlFile.load_mxl(mxl_path)
    
    for part in mxl_file.tree.getroot().findall("part"):
        # linearize all at once
        full_linearizer = Linearizer()
        full_linearizer.process_part(part)

        # split the xml
        pages = split_part_to_systems(part)
        assert len(pages) == len(full_linearizer.output_tokens)

        # check all pages and systems match system-wise linearization
        for pi, page in enumerate(pages):
            for si, system in enumerate(page.systems):
                system_linearizer = Linearizer()
                system_linearizer.process_part(system.part)
                assert len(system_linearizer.output_tokens) == 1
                assert len(system_linearizer.output_tokens[0]) == 1
                system_tokens = system_linearizer.output_tokens[0][0]
                
                tokens_from_full = full_linearizer.output_tokens[pi][si]

                if system_tokens != tokens_from_full:
                    print("NEW", system_tokens[:12])
                    print("OLD", tokens_from_full[:12])
                    print(ET.tostring(system.part.find("measure/attributes")))
                    print()
                # assert system_tokens == tokens_from_full

    # break
