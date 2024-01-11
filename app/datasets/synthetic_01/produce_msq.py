import os
from typing import Iterable
from app.symbolic.MxlFile import MxlFile
from app.symbolic.Mxl2Msq import Mxl2Msq
from app.symbolic.split_part_to_systems import split_part_to_systems
from .config import *


def produce_msq(
    score_ids: Iterable[int],
    slice_index: int,
    slice_count: int
):
    errors_file_path = os.path.join(
        DATASET_PATH,
        f"msq_errors_{slice_index}of{slice_count}.txt"
    )
    vocabulary_file_path = os.path.join(
        DATASET_PATH,
        f"vocabulary_{slice_index}of{slice_count}.txt"
    )

    msq_vocabulary = set()

    with open(errors_file_path, "w") as errout:
        for score_id in score_ids:
            mxl_path = os.path.join(DATASET_PATH, "mxl", f"{score_id}.mxl")

            print("Converting to MSQ:", mxl_path, "...")

            print("\n\n", file=errout)
            print("#" * (len(mxl_path) + 4), file=errout)
            print("# " + mxl_path + " #", file=errout)
            print("#" * (len(mxl_path) + 4), file=errout)
            
            mxl = MxlFile.load_mxl(mxl_path)
            part = mxl.get_piano_part()

            for (page_number, system_number), system in split_part_to_systems(part):
                convertor = Mxl2Msq(errout=errout)
                msq = convertor.process_part(system)
                msq_vocabulary.update(convertor.msq_tokens)
                
                msq_path = os.path.join(
                    DATASET_PATH, "samples", str(score_id),
                    f"p{page_number}-s{system_number}.msq"
                )
                os.makedirs(os.path.dirname(msq_path), exist_ok=True)
                with open(msq_path, "w") as file:
                    print(msq, file=file)

    with open(vocabulary_file_path, "w") as file:
        for token in sorted(msq_vocabulary):
            print(token, file=file)
    
    print(msq_vocabulary)