import os
import yaml
import cv2
from .produce_lmx import produce_lmx
from .config import *
from .musescore_conversion import musescore_conversion


def build():

    # get all the scores to build
    with open(TESTSET_SCORES_YAML) as file:
        scores = yaml.safe_load(file)

    # TODO: DEBUG: take only first two
    scores = dict(list(scores.items())[0:2])

    # prepare MXL and PNG files
    # (png files for comparison during manual annotation)
    musescore_conversion(scores)

    # produce LMX files
    produce_lmx(scores.keys(), extended_flavor=False)
    produce_lmx(scores.keys(), extended_flavor=True)
    
    # export samples
    for score_id, score in scores.items():
        print("Processing", score_id, "...")

        score_dir = os.path.join(DATASET_PATH, "samples", str(score_id))

        # clear the samples folder
        assert os.system(f"rm -rf {score_dir}/*") == 0
        assert os.system(f"mkdir -p {score_dir}") == 0

        # get the defined mapping
        mappings_path = os.path.join(
            DATASET_PATH, "corpus_to_imslp", str(score_id) + ".yaml"
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
    # copy LMX files
    assert os.system(
        f"cp {DATASET_PATH}/lmx/{sample}.core.lmx " + \
            f"{DATASET_PATH}/samples/{sample}.core.lmx"
    ) == 0
    assert os.system(
        f"cp {DATASET_PATH}/lmx/{sample}.extended.lmx " + \
            f"{DATASET_PATH}/samples/{sample}.extended.lmx"
    ) == 0

    # extract mapping data
    imslp_id = mapping["imslpDocument"][1:] # without hash
    imslp_page = mapping["imslpPage"]
    imslp_system = mapping["imslpSystem"]

    # load the imslp systems map
    systems_path = os.path.join(
        DATASET_PATH, "imslp_systems", "IMSLP" + imslp_id + ".yaml"
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

    # get the bounding box and image path
    png_path = os.path.join(DATASET_PATH, "imslp_pngs", *page["image"].split("/"))
    img = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)
    bbox = system["boundingBox"]
    img_height, img_width = img.shape

    # bbox to numbers
    x1 = bbox["left"]
    x2 = bbox["left"] + bbox["width"]
    y1 = bbox["top"]
    y2 = bbox["top"] + bbox["height"]
    height = y2 - y1

    # grow the bbox to cropbox
    vertical_margin=0.5 # in the multiples of system height
    horizontal_margin=0.5 # in the multiples of system height
    x1 -= horizontal_margin * height
    x2 += horizontal_margin * height
    y1 -= vertical_margin * height
    y2 += vertical_margin * height

    # hit page border
    x1 = max(x1, 0)
    y1 = max(y1, 0)
    x2 = min(x2, img_width - 1)
    y2 = min(y2, img_height - 1)

    # round to pixel
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    
    # crop the image
    sample_image = img[y1:y2,x1:x2]

    # invert the image
    if page.get("invertImage", False):
        pass

    # save the image
    sample_path = os.path.join(DATASET_PATH, "samples", sample + ".png")
    cv2.imwrite(sample_path, sample_image)
