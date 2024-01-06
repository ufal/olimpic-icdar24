import os
import yaml


SKIP = set([
    # freezes MuseScore, cannot be openned, no crash, no nothing
    6264558, # datasets/OpenScore-Lieder/scores/Chaminade,_Cécile/_/Ballade_à_la_lune
])


def prepare_open_score_lieder():
    data = yaml.safe_load(
        open("datasets/OpenScore-Lieder/data/scores.yaml", "r")
    )
    for index, (id, record) in enumerate(data.items()):
        directory_path = os.path.join(
            "datasets/OpenScore-Lieder/scores",
            record["path"]
        )
        mscx_path = os.path.join(directory_path, f"lc{id}.mscx")
        mxl_path = os.path.join(directory_path, f"lc{id}.mxl")
        svg_path = os.path.join(directory_path, f"lc{id}.svg")

        print(f"{index}/{len(data)}", id, directory_path)

        if id in SKIP:
            print("Skipping due to an exception in place.")
            continue

        if not os.path.exists(mxl_path):
            exit_code = os.system(f"musescore/musescore.AppImage '{mscx_path}' -o '{mxl_path}'")
            assert exit_code == 0
        else:
            print("Skipping MXL - already there.")
        
        if not os.path.exists(svg_path.replace(".svg", "-1.svg")):
            exit_code = os.system(f"musescore/musescore.AppImage '{mscx_path}' -o '{svg_path}'")
            assert exit_code == 0
        else:
            print("Skipping SVG - already there.")
