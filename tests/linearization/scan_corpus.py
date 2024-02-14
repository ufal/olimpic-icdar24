import glob
import sys
from app.linearization.Linearizer import Linearizer
from app.linearization.Delinearizer import Delinearizer
from app.symbolic.MxlFile import MxlFile
from app.symbolic.Pruner import Pruner
from app.symbolic.actual_durations_to_fractional import actual_durations_to_fractional
from app.symbolic.debug_compare import compare_parts


def scan_corpus():
    mxl_files = glob.glob(
        "datasets/OpenScore-Lieder/scores/**/*.mxl",
        recursive=True
    )
    mxl_files.sort()

    for path in mxl_files:
        print(path, "...")
        scan_mxl_file(path)


def scan_mxl_file(path: str):
    pruner = Pruner(
        prune_durations=False, # durations depend on divisions
    )

    mxl = MxlFile.load_mxl(path)
    for part in mxl.tree.findall("part"):
        linearizer = Linearizer() # errout=sys.stdout
        linearizer.process_part(part)

        text = " ".join(linearizer.output_tokens)
        delinearizer = Delinearizer(
            errout=sys.stdout,
            keep_fractional_durations=True
        )
        delinearizer.process_text(text)

        # prune to the LXM element subset
        pruner.process_part(part)
        pruner.process_part(delinearizer.part_element)
        
        # turn gold to fractional durations
        actual_durations_to_fractional(part)
        
        compare_parts(
            expected=part,
            given=delinearizer.part_element
        )
