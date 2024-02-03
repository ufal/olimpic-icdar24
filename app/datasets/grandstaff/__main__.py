import argparse
import os
from .remove_problematic import remove_problematic
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
    "remove-problematic",
    aliases=[],
    help="Removes problematic scores from the dataset"
)

build_parser=subparsers.add_parser(
    "build",
    aliases=[],
    help="Generates LMX and MusicXML annotations for each sample"
)
build_parser.add_argument(
    "--slice_index", type=int, default=0
)
build_parser.add_argument(
    "--slice_count", type=int, default=1
)
build_parser.add_argument(
    "--soft", action="store_true", default=False,
    help="Skips processing for already processed files"
)


########
# Main #
########

args = parser.parse_args()

# annotation commans
if args.command_name == "remove-problematic":
    remove_problematic()
elif args.command_name == "build":
    build(
        slice_index=args.slice_index,
        slice_count=args.slice_count,
        soft=args.soft
    )
else:
    parser.print_help()
    exit(2)
