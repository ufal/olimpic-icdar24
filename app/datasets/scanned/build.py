import os
import yaml
from ..config import SCANNED_DATASET_PATH
from ..musescore_corpus_conversion import musescore_corpus_conversion
from ..prepare_corpus_lmx_and_musicxml import prepare_corpus_lmx_and_musicxml
from ..take_scores import take_scores
from ..transfer_samples import transfer_samples
from ..crop_system_from_png_page import crop_system_from_png_page
from .prepare_imslp_pngs import prepare_imslp_pngs
from typing import Optional


def build(
    slice_index: int,
    slice_count: int,
    inspect: Optional[int],
    linearize_only: bool,
    soft: bool
):
    scores, slice_index, slice_count = take_scores(
        train=False,
        dev=True,
        test=True,
        slice_index=slice_index,
        slice_count=slice_count,
        inspect=inspect
    )

    # prepare corpus MXL files
    musescore_corpus_conversion(scores=scores, format="mxl", soft=soft)

    # split xml files into systems and convert to sequences
    prepare_corpus_lmx_and_musicxml(scores=scores, soft=soft)

    # copy samples
    transfer_samples(
        scores=scores,
        corpus_glob="lmx/*.lmx",
        dataset_folder=SCANNED_DATASET_PATH
    )
    transfer_samples(
        scores=scores,
        corpus_glob="musicxml/*.musicxml",
        dataset_folder=SCANNED_DATASET_PATH
    )

    # if we only linearize, we are done
    if linearize_only:
        return

    # make sure all IMSLP PNGs are extracted
    prepare_imslp_pngs()
    
    # crop out PNG images
    for score_id, score in scores.items():
        print("Cropping out PNG systems for", score_id, "...")

        # get the defined mapping
        mappings_path = os.path.join(
            SCANNED_DATASET_PATH, "corpus_to_imslp", str(score_id) + ".yaml"
        )
        if not os.path.isfile(mappings_path):
            print("[ERROR] Missing the mappings file:", mappings_path)
            continue
        with open(mappings_path) as file:
            mappings = yaml.safe_load(file)
        
        # go through all the defined system mappings
        for sample, mapping in mappings.items():
            process_sample(sample, mapping)


def process_sample(sample: str, mapping):
    # extract mapping data
    imslp_id = mapping["imslpDocument"][1:] # without hash
    imslp_page = mapping["imslpPage"]
    imslp_system = mapping["imslpSystem"]

    # load the imslp systems map
    systems_path = os.path.join(
        SCANNED_DATASET_PATH, "imslp_systems", "IMSLP" + imslp_id + ".yaml"
    )
    if not os.path.isfile(systems_path):
        print("[ERROR] Missing IMSLP systems file:", systems_path)
        return
    with open(systems_path) as file:
        systems_map = yaml.safe_load(file)
    pages = systems_map["pages"]
    if imslp_page not in pages:
        print(f"[ERROR] Page {imslp_page} not found in", systems_path)
        return
    page = pages[imslp_page]
    systems = page["systems"]
    if imslp_system > len(systems):
        print(f"[ERROR] System {imslp_system} not found in page {imslp_page} in", systems_path)
        return
    system = systems[imslp_system - 1] # one-indexed

    # get the bounding box
    bbox = system["boundingBox"]

    crop_system_from_png_page(
        page_png=os.path.join(SCANNED_DATASET_PATH, "imslp_pngs", *page["image"].split("/")),
        bbox=(
            bbox["left"],
            bbox["top"],
            bbox["left"] + bbox["width"],
            bbox["top"] + bbox["height"]
        ),
        out_system_png=os.path.join(SCANNED_DATASET_PATH, "samples", sample + ".png")
    )

