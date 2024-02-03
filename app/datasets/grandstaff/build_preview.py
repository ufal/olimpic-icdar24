import os
import random
from ...linearization.vocabulary import *
from ..config import GRANDSTAFF_DATASET_PATH
import glob


def build_preview():
    preview_folder = GRANDSTAFF_DATASET_PATH + "-preview"

    # clear the folder first
    assert os.system(f"rm -rf \"{preview_folder}\"") == 0
    assert os.system(f"mkdir \"{preview_folder}\"") == 0

    # load files to parse
    paths = glob.glob(
        os.path.join(GRANDSTAFF_DATASET_PATH, "**/*.lmx"),
        recursive=True
    )
    paths = list(sorted(path[:-len(".lmx")] for path in paths))

    # take 100 random samples
    rng = random.Random(42)
    rng.shuffle(paths)
    paths = paths[:100]

    # build the index.html
    with open(os.path.join(preview_folder, "index.html"), "w") as html:
        html.write(f"""<!DOCTYPE html><html>
            <head>
                <meta charset='utf-8'>
                <title>{GRANDSTAFF_DATASET_PATH}</title>
            </head>
            <body>
                <h1>{GRANDSTAFF_DATASET_PATH}</h1>
        """)
        for i, path in enumerate(paths):
            preview_jpg_path = str(i) + ".jpg"

            # copy the PNG file
            assert os.system(
                f"cp {path}.jpg {preview_folder}/{preview_jpg_path}"
            ) == 0

            # load annotations
            annotation = prepare_annotaion_html(path + ".lmx")

            sample = os.path.relpath(path, GRANDSTAFF_DATASET_PATH)
            html.write(f"""
                <p>
                    <b>Sample:</b> {sample}<br>
                    <b>Image:</b> {sample}.jpg<br>
                    <img src="{preview_jpg_path}" style="height: 256px"/><br>
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
