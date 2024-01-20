import os
from typing import Iterable
from app.symbolic.MxlFile import MxlFile
from app.symbolic.Mxl2Msq import Mxl2Msq
from app.symbolic.split_part_to_systems import split_part_to_systems
from .config import *
from ...linearization.Linearizer import Linearizer


def produce_lmx(
    score_ids: Iterable[int],
    extended_flavor: bool
):
    for score_id in score_ids:
        mxl_path = os.path.join(DATASET_PATH, "mxl", f"{score_id}.mxl")

        print("Converting to LMX:", mxl_path, "...")
        
        mxl = MxlFile.load_mxl(mxl_path)
        part = mxl.get_piano_part()

        linearizer = Linearizer(extended_flavor=extended_flavor)
        linearizer.process_part(part)

        flavor = "extended" if extended_flavor else "core"

        for pi, page in enumerate(linearizer.output_tokens):
            page_number = str(pi + 1)
            for si, system in enumerate(page):
                system_number = str(si + 1)
            
                lmx_path = os.path.join(
                    DATASET_PATH, "samples", str(score_id),
                    f"p{page_number}-s{system_number}.{flavor}.lmx"
                )
                os.makedirs(os.path.dirname(lmx_path), exist_ok=True)
                with open(lmx_path, "w") as file:
                    print(" ".join(system), file=file)
    