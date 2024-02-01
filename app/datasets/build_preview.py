import os
import random
from ..linearization.vocabulary import *


def build_preview(
    dataset_path: str,
    slice_name: str
):
    preview_folder = os.path.join(dataset_path, "preview")

    # clear the folder first
    assert os.system(f"rm -rf \"{preview_folder}\"") == 0
    assert os.system(f"mkdir \"{preview_folder}\"") == 0

    # load samples
    with open(os.path.join(dataset_path, f"samples.{slice_name}.txt"), "r") as file:
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
                <title>{dataset_path}</title>
            </head>
            <body>
                <h1>{dataset_path} ({slice_name})</h1>
        """)
        for sample in samples:
            preview_png_path = sample.replace("/", "_") + ".png"

            # copy the PNG file
            assert os.system(
                f"cp {dataset_path}/{sample}.png {preview_folder}/{preview_png_path}"
            ) == 0

            # load annotations
            annotation = prepare_annotaion_html(
                os.path.join(dataset_path, sample + ".lmx")
            )

            html.write(f"""
                <p>
                    <b>Sample:</b> {sample}<br>
                    <b>Image:</b> {sample}.png<br>
                    <img src="{preview_png_path}" style="height: 256px"/><br>
                    <br>
                    <b>LMX:</b> {sample}.lmx<br>
                    {annotation}<br>
                </p>
                <hr/>
            """)
        
        html.write(f"""</body></html>""")


def prepare_annotaion_html(path: str) -> str:
    with open(path) as file:
        tokens = file.readlines()[0].split()
    
    processed_tokens = []
    for i, token in enumerate(tokens):
        if token == "measure":
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
