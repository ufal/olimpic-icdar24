import argparse
import os
from .build import build
from ..config import GRANDSTAFF_DATASET_PATH
from .check_correspondence import check_correspondence
from .build_preview import build_preview


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
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

subparsers.add_parser(
    "build-preview",
    aliases=[],
    help="Builds the preview html folder"
)


########
# Main #
########

args = parser.parse_args()

# annotation commans
if args.command_name == "build":
    build(
        slice_index=args.slice_index,
        slice_count=args.slice_count,
        soft=args.soft
    )
elif args.command_name == "tar-dataset":
    tar_path = os.path.realpath(GRANDSTAFF_DATASET_PATH + "-lmx.tgz")
    assert os.system(
        f"cd {GRANDSTAFF_DATASET_PATH} && tar -czvf {tar_path} " +
            f"beethoven/ " +
            f"chopin/ " +
            f"hummel/ " +
            f"joplin/ " +
            f"mozart/ " +
            f"scarlatti-d/ " +
            f"README.txt " +
            f"samples.train.txt " +
            f"samples.dev.txt " +
            f"samples.test.txt"
    ) == 0
elif args.command_name == "check-correspondence":
    check_correspondence()
elif args.command_name == "build-preview":
    build_preview()
else:
    parser.print_help()
    exit(2)
