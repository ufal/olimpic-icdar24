import os
from ..config import SCANNED_DATASET_PATH
from ..splits.data import *
from ..check_sample_pairing import check_sample_pairing
from ..build_dataset_index import build_dataset_index
from ..compute_dataset_statistics import compute_dataset_statistics
from ...linearization.vocabulary import print_vocabulary


def finalize():

    # check that LMX, MusicXML, and PNG files are paired correctly
    check_sample_pairing(scores=DEV_SCORES, dataset_path=SCANNED_DATASET_PATH)
    check_sample_pairing(scores=TEST_SCORES, dataset_path=SCANNED_DATASET_PATH)

    # build indexes
    build_dataset_index(
        scores=DEV_SCORES,
        slice_name="dev",
        dataset_path=SCANNED_DATASET_PATH
    )
    build_dataset_index(
        scores=TEST_SCORES,
        slice_name="test",
        dataset_path=SCANNED_DATASET_PATH
    )

    # compute statistics
    compute_dataset_statistics(slice_name="dev", dataset_path=SCANNED_DATASET_PATH)
    compute_dataset_statistics(slice_name="test", dataset_path=SCANNED_DATASET_PATH)

    # create vocabulary file
    vocabulary_file_path = os.path.join(SCANNED_DATASET_PATH, "vocabulary.txt")
    with open(vocabulary_file_path, "w") as file:
        print_vocabulary(file=file)
