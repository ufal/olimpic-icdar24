from typing import Dict, Any
import os
import tempfile
import json
from .config import LIEDER_CORPUS_PATH, MSCORE


def musescore_corpus_conversion(
    scores: Dict[int, Dict[str, Any]],
    format="mxl",
    soft=False
):
    """Executes MuseScore batch conversion on the OpenScore-Lieder corpus for selected scores"""

    # create the conversion json file
    conversion = []
    for score_id, score in scores.items():
        score_folder = os.path.join(
            LIEDER_CORPUS_PATH, "scores", score["path"]
        )
        out_path = os.path.join(score_folder, f"lc{score_id}.{format}")

        # skip already exported files
        if soft:
            if os.path.isfile(out_path):
                continue
            if os.path.isfile(out_path.replace(f".{format}", f"-1.{format}")):
                continue
            if os.path.isfile(out_path.replace(f".{format}", f"-01.{format}")):
                continue

        conversion.append({
            "in": os.path.join(score_folder, f"lc{score_id}.mscx"),
            "out": out_path
        })
    
    if len(conversion) == 0:
        return
    
    # run musescore conversion
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False)
    try:
        json.dump(conversion, tmp)
        tmp.close()

        # clear musescore settings, since it may remember not to print
        # page and system breaks, but we do want those to be printed
        assert os.system(
            f"rm -f ~/.config/MuseScore/MuseScore3.ini"
        ) == 0

        assert os.system(
            f"{MSCORE} -j \"{tmp.name}\""
        ) == 0
    finally:
        tmp.close()
        os.unlink(tmp.name)
