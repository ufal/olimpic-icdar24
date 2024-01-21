import os
import sys
import random
from .config import *
from ...linearization.vocabulary import *


def build_preview():
    preview_folder = os.path.join(DATASET_PATH, "preview")

    # clear the folder first
    assert os.system(f"rm -rf {preview_folder}") == 0
    assert os.system(f"mkdir {preview_folder}") == 0

    # load test samples
    with open(os.path.join(DATASET_PATH, "samples.all.txt"), "r") as file:
        samples = [line.strip() for line in file.readlines()]
    
    # take 100 random samples
    rng = random.Random(42)
    rng.shuffle(samples)
    samples = samples[:100]

    # build the index.html
    with open(os.path.join(preview_folder, "index.html"), "w") as html:
        html.write(f"""<!DOCTYPE html><html>
            <head>
                <meta charset='utf-8'>
                <title>{DATASET_PATH}</title>
            </head>
            <body>
                <h1>{DATASET_PATH}</h1>
        """)
        for sample in samples:
            preview_png_path = sample.replace("/", "_") + ".png"

            # copy the PNG file
            assert os.system(
                f"cp {DATASET_PATH}/{sample}.png {preview_folder}/{preview_png_path}"
            ) == 0

            # load annotations
            core_annotation = prepare_annotaion_html(
                os.path.join(DATASET_PATH, sample + ".core.lmx")
            )
            extended_annotation = prepare_annotaion_html(
                os.path.join(DATASET_PATH, sample + ".extended.lmx")
            )

            html.write(f"""
                <p>
                    <b>Sample:</b> {sample}<br>
                    <b>Image:</b> {sample}.png<br>
                    <img src="{preview_png_path}" style="height: 256px"/><br>
                    <br>
                    <b>Core LMX:</b> {sample}.core.lmx<br>
                    {core_annotation}<br>
                    <br>
                    <b>Extended LMX:</b> {sample}.extended.lmx<br>
                    {extended_annotation}<br>
                </p>
                <hr/>
            """)
        
        html.write(f"""</body></html>""")


def prepare_annotaion_html(path: str) -> str:
    with open(path) as file:
        tokens = file.readlines()[0].split()
    
    processed_tokens = []
    for i, token in enumerate(tokens):
        if token in EXTENDED_FLAVOR_TOKENS:
            token = "<span style=\"background: cyan\">" + token + "</span>"

        elif token == "measure":
            token = "<b><u>" + token + "</u></b>"
            if i != 0:
                token = "<br/>" + token
        elif token in ["backup", "forward"]:
            token = "<b>" + token + "</b>"
        elif token in NOTE_ROOT_TOKENS or token in TIME_MODIFICATION_TOKENS:
            token = "<u>" + token + "</u>"
        elif token in NOTE_PREFIX_TOKENS:
            token = "<sub>" + token + "</sub>"
        elif token in NOTE_SUFFIX_TOKENS:
            token = "<sup>" + token + "</sup>"

        processed_tokens.append(token)
    
    return " ".join(processed_tokens)
