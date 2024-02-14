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

linearize_parser = subparsers.add_parser(
    "linearize",
    aliases=[],
    help="Generates an LMX file from a MusicXML file"
)
linearize_parser.add_argument(
    "filename",
    type=str,
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

from .Linearizer import Linearizer
from .Delinearizer import Delinearizer
from ..symbolic.MxlFile import MxlFile
import xml.etree.ElementTree as ET
from ..symbolic.part_to_score import part_to_score


def linearize(filename: str):
    if filename == "-":
        input_xml = sys.stdin.readline()
        mxl = MxlFile(ET.ElementTree(
            ET.fromstring(input_xml))
        )
    elif filename.endswith(".mxl"):
        mxl = MxlFile.load_mxl(filename)
    else:
        with open(filename, "r") as f:
            input_xml = f.readline()
            mxl = MxlFile(ET.ElementTree(
                ET.fromstring(input_xml))
            )
    
    try:
        part = mxl.get_piano_part()
    except:
        part = mxl.tree.find("part")
    
    if part is None or part.tag != "part":
        print("No <part> element found.", file=sys.stderr)
        exit()
    
    linearizer = Linearizer(
        errout=sys.stderr
    )
    linearizer.process_part(part)
    output_lmx = " ".join(linearizer.output_tokens)
    
    if filename == "-":
        print(output_lmx)
    else:
        with open(os.path.splitext(filename) + ".musicxml", "r") as f:
            print(output_lmx, file=f)


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
if args.command_name == "linearize":
    linearize(args.filename)
elif args.command_name == "delinearize":
    delinearize(args.filename)
else:
    parser.print_help()
    exit(2)
