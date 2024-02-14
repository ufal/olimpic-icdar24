import argparse
import os
import glob
import json
from .scan_corpus import scan_corpus


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

subparsers.add_parser(
    "convert-test-samples",
    aliases=[],
    help="Converts MuseScore test samples to MusicXML samples"
)

subparsers.add_parser(
    "convert-corpus",
    aliases=[],
    help="Converts MuseScore files to MXL files in the OS Lieder corpus"
)

subparsers.add_parser(
    "scan-corpus",
    aliases=[],
    help="Executes the linearizer on the entire OpenScore Lieder corpus"
)

subparsers.add_parser(
    "print-vocabulary",
    aliases=[],
    help="Prints the current vocabulary"
)


########
# Main #
########

args = parser.parse_args()

if args.command_name == "convert-test-samples":
    samples_dir = os.path.join(os.path.dirname(__file__), "samples")
    samples = glob.glob(os.path.join(samples_dir, "**/*.mscz"))
    conversions = []
    for sample in samples:
        sample = os.path.relpath(sample, os.path.curdir)
        conversions.append({
            "in": sample,
            "out": sample.replace(".mscz", ".xml")
        })
    conversion_filename = os.path.join(samples_dir, "conversions.json")
    with open(conversion_filename, "w") as f:
        json.dump(conversions, f, indent=2)
    assert os.system(
        f"musescore/musescore.AppImage -j {conversion_filename}"
    ) == 0

elif args.command_name == "convert-corpus":
    os.chdir("datasets/OpenScore-Lieder/data")
    assert os.system(
        f"../../../musescore/musescore.AppImage -j corpus_conversion.json"
    ) == 0

elif args.command_name == "scan-corpus":
    scan_corpus()

elif args.command_name == "print-vocabulary":
    from app.linearization.vocabulary import ALL_TOKENS
    print("\n".join(ALL_TOKENS))
    print("-------------------")
    print("TOTAL TOKENS:", len(ALL_TOKENS))

else:
    parser.print_help()
    exit(2)
