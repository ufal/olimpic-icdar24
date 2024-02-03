import argparse
import os
from .remove_problematic import remove_problematic
from .build import build
from ..config import GRANDSTAFF_DATASET_PATH
from .check_correspondence import check_correspondence


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

subparsers.add_parser(
    "tar-dataset",
    aliases=[],
    help="Packages the resulting dataset in a tar file"
)

subparsers.add_parser(
    "check-correspondence",
    aliases=[],
    help="Checks that for each .krn file there is a .musicxml and .lmx file"
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
elif args.command_name == "tar-dataset":
    tar_path = os.path.realpath(GRANDSTAFF_DATASET_PATH + "-extended.tgz")
    assert os.system(
        f"cd {GRANDSTAFF_DATASET_PATH} && tar -czvf {tar_path} " +
            f"beethoven/ " +
            f"chopin/ " +
            f"hummel/ " +
            f"joplin/ " +
            f"mozart/ " +
            f"scarlatti-d/"
    ) == 0
elif args.command_name == "check-correspondence":
    check_correspondence()
else:
    parser.print_help()
    exit(2)
