import argparse
import sys
import os


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

delinearize_parser = subparsers.add_parser(
    "delinearize",
    aliases=[],
    help="Generates a MusicXML file from an LMX file"
)
delinearize_parser.add_argument(
    "filename",
    type=str,
)


###################
# Implementations #
###################

from .Delinearizer import Delinearizer
import xml.etree.ElementTree as ET
from ..symbolic.part_to_score import part_to_score


def delinearize(filename: str):
    if filename == "-":
        input_lmx = sys.stdin.readline()
    else:
        with open(filename, "r") as f:
            input_lmx = f.readline()

    delinearizer = Delinearizer(
        errout=sys.stderr
    )
    delinearizer.process_text(input_lmx)
    score_etree = part_to_score(delinearizer.part_element)
    output_xml = str(ET.tostring(
        score_etree.getroot(),
        encoding="utf-8",
        xml_declaration=True
    ), "utf-8")

    if filename == "-":
        print(output_xml)
    else:
        with open(os.path.splitext(filename) + ".musicxml", "r") as f:
            print(output_xml, file=f)



########
# Main #
########

args = parser.parse_args()

# annotation commans
if args.command_name == "delinearize":
    delinearize(args.filename)
else:
    parser.print_help()
    exit(2)
