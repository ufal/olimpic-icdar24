import argparse
import unittest
import os
import sys
import glob
import json


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

build_parser = subparsers.add_parser(
    "run",
    aliases=[],
    help="Executes all the available unit tests."
)

build_parser = subparsers.add_parser(
    "convert",
    aliases=[],
    help="Converts MuseScore samples to MusicXML samples"
)


########
# Main #
########

args = parser.parse_args()

if args.command_name == "run":
    suite = unittest.TestLoader().discover(
        start_dir=os.path.dirname(__file__),
        top_level_dir=os.path.join(os.path.dirname(__file__), "../../"),
        pattern="*Test.py"
    )
    unittest.TextTestRunner(verbosity=2).run(suite)

elif args.command_name == "convert":
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

else:
    parser.print_help()
    exit(2)
