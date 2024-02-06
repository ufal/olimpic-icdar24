import os
from ...datasets.config import SCANNED_DATASET_PATH
from ..TEDn_lmx_xml import TEDn_lmx_xml
import sys


total_gold = 0
total_cost = 0


def scan_testset(tedn_flavor: str):
    samples_path = os.path.join(SCANNED_DATASET_PATH, "samples.test.txt")
    with open(samples_path) as file:
        for line in file:
            sample_path = os.path.join(SCANNED_DATASET_PATH, line.strip())
            process_sample(sample_path, tedn_flavor)


def process_sample(sample_path: str, tedn_flavor: str):
    global total_gold, total_cost

    print(sample_path, "...")
    
    with open(sample_path + ".lmx") as file:
        lmx_string = file.read()
    with open(sample_path + ".musicxml") as file:
        musicxml_string = file.read()
    
    # run the TEDn function
    result = TEDn_lmx_xml(
        predicted_lmx=lmx_string,
        gold_musicxml=musicxml_string,
        flavor=tedn_flavor,
        debug=True,
        errout=sys.stdout
    )
    total_gold += result.gold_cost
    total_cost += result.edit_cost
    print("[SAMPLE] TEDn error:", round(result.normalized_edit_cost * 100, 2), "%")
    print("[TOTAL] TEDn error: ", round((total_cost / total_gold) * 100, 2), "% ...", total_cost, "/", total_gold)
