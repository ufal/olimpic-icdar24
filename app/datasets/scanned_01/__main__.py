import argparse
from .load_workbench import load_workbench
from .save_workbench import save_workbench
from .prepare_imslp import prepare_imslp
from .build import build


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

subparsers.add_parser(
    "prepare-imslp",
    aliases=[],
    help="Converts IMSLP PDFs to images and checks their presence"
)

subparsers.add_parser(
    "build",
    aliases=[],
    help="Builds samples from the manually created annotation files"
)

load_wb_parser = subparsers.add_parser(
    "load-workbench",
    aliases=[],
    help="Creates the workbench inkscape file for a given corpus score ID"
)
load_wb_parser.add_argument(
    "score_id",
    type=int,
    help="ID of a corpus score"
)

load_wb_parser = subparsers.add_parser(
    "save-workbench",
    aliases=[],
    help="Creates the workbench inkscape file for a given corpus score ID"
)


########
# Main #
########

args = parser.parse_args()

if args.command_name == "prepare-imslp":
    prepare_imslp()
elif args.command_name == "build":
    build()
elif args.command_name == "load-workbench":
    load_workbench(args.score_id)
elif args.command_name == "save-workbench":
    save_workbench()
else:
    parser.print_help()
    exit(2)
