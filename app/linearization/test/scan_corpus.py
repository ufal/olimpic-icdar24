import glob
import os
import sys
from ..Linearizer import Linearizer
from ...symbolic.MxlFile import MxlFile


# Error report:
# ~65 of files contain some error, most of them only a few notes
# There are a few files that have more than 40 errors and it's these:
#
# - Holmès,_Augusta_Mary_Anne/Mélodies_pour_piano_et_chant/19_Un_rêve, à_2_voix/lc6017382.mxl
# - Corder,_Frederick/_/O_Sun,_That_Wakenest/lc6480349.mxl
# - Jaëll,_Marie/Les_Orientales/4_Les_tronçons_du_serpent/lc6217375.mxl
# - Jaëll,_Marie/4_Mélodies/3_Les_petits_oiseaux/lc5840072.mxl
# - Bizet,_Georges/20_Mélodies,_Op.21/17_Chant_d’amour!/lc6903010.mxl
#
# I recommend removing these from all the datasets.
# It's these IDs: 6017382, 6480349, 6217375, 5840072, 6903010


def scan_corpus(extended_flavor=True):
    mxl_files = glob.glob(
        "datasets/OpenScore-Lieder/scores/**/*.mxl",
        recursive=True
    )

    for path in mxl_files:
        print(path, "...")
        scan_mxl_file(path, extended_flavor)
        # break


def scan_mxl_file(path: str, extended_flavor: bool):
    # score_id = os.path.basename(path)[2:-4] # strip "lc" and ".mxl"
    # flavor = "extended" if extended_flavor else "core"

    mxl = MxlFile.load_mxl(path)
    for part in mxl.tree.findall("part"):
        linearizer = Linearizer(errout=sys.stdout)
        linearizer.process_part(part)
