from typing import List
import glob
import os
import re
from .constants import *


def print_pdfs(all_scores, score_ids: List[int]):
    assert os.path.isdir(SCANNED_DATASET_PATH), "Set up the scanned dataset"
    downloaded_pdfs = glob.glob(f"{SCANNED_DATASET_PATH}/imslp_pdfs/*.pdf")
    downloaded_pdfs = {
        "#" + re.match("^IMSLP(\d+)", os.path.basename(path))[1]: os.path.basename(path)
        for path in downloaded_pdfs
    }

    # group scores to pdfs
    pdfs_to_print = set()
    for score_id in score_ids:
        score = all_scores[score_id]
        pdfs_to_print.add(score["imslp"].strip())
    pdfs_to_print = list(sorted(pdfs_to_print))
    
    for i, imslp_id in enumerate(pdfs_to_print):
        is_downloaded = imslp_id in downloaded_pdfs
        print(
            (str(i + 1) + ")").rjust(4),
            "[x]" if is_downloaded else "[ ]",
            imslp_id.ljust(8),
            ("https://imslp.org/wiki/Special:ReverseLookup/" + imslp_id[1:]).ljust(55),
            downloaded_pdfs.get(imslp_id)
        )