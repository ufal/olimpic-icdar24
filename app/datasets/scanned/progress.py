from ..splits.data import *
from ..config import SCANNED_DATASET_PATH
import glob
import re


def progress():
    """Prints the annotation progress for the scanned test and dev partitions"""

    print("##################")
    print("# Test partition #")
    print("##################")
    print()

    print("Scores")
    print("------")
    print_scores(TEST_SCORES)
    print()

    print("IMSLP PDFs")
    print("----------")
    print_pdfs(TEST_SCORES)
    print()

    print("#################")
    print("# Dev partition #")
    print("#################")
    print()

    print("Scores")
    print("------")
    print_scores(DEV_SCORES)
    print()

    print("IMSLP PDFs")
    print("----------")
    print_pdfs(DEV_SCORES)
    print()


def print_scores(scores):
    assert os.path.isdir(SCANNED_DATASET_PATH), "Set up the scanned dataset"
    annotated_scores = glob.glob(f"{SCANNED_DATASET_PATH}/corpus_to_imslp/*.yaml")
    annotated_scores = set(
        int(os.path.basename(path)[:-5])
        for path in annotated_scores
    )
    
    for i, (score_id, score) in enumerate(scores.items()):
        is_annotated = score_id in annotated_scores
        print(
            (str(i + 1) + ")").rjust(4),
            "[x]" if is_annotated else "[ ]",
            score_id,
            score["path"]
        )


def print_pdfs(scores):
    assert os.path.isdir(SCANNED_DATASET_PATH), "Set up the scanned dataset"
    downloaded_pdfs = glob.glob(f"{SCANNED_DATASET_PATH}/imslp_pdfs/*.pdf")
    downloaded_pdfs = {
        "#" + re.match("^IMSLP(\d+)", os.path.basename(path))[1]: os.path.basename(path)
        for path in downloaded_pdfs
    }

    # group scores to pdfs
    pdfs_to_print = set(
        score["imslp"].strip() for score in scores.values()
    )
    
    for i, imslp_id in enumerate(pdfs_to_print):
        is_downloaded = imslp_id in downloaded_pdfs
        print(
            (str(i + 1) + ")").rjust(4),
            "[x]" if is_downloaded else "[ ]",
            imslp_id.ljust(8),
            ("https://imslp.org/wiki/Special:ReverseLookup/" + imslp_id[1:]).ljust(55),
            downloaded_pdfs.get(imslp_id)
        )