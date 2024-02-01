import argparse
import os
from .build import build
from .finalize import finalize
from ..build_preview import build_preview
from ..config import SYNTHETIC_DATASET_PATH


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

build_parser = subparsers.add_parser(
    "build",
    aliases=[],
    help="Prepare the dataset",
    description=
        "Builds the dataset up from the downloaded Open Score " + \
        "Lieder corpus."
)
build_parser.add_argument(
    "--slice_index", type=int, default=0
)
build_parser.add_argument(
    "--slice_count", type=int, default=1
)
build_parser.add_argument(
    "--inspect", type=int, default=None,
    help="Inspect just a single score"
)
build_parser.add_argument(
    "--linearize_only", action="store_true", default=False,
    help="Only process the semantic data, not images (MXL, LMX)"
)
build_parser.add_argument(
    "--soft", action="store_true", default=False,
    help="Skips processing for already processed files"
)

subparsers.add_parser(
    "finalize",
    aliases=[],
    help="Finalize build",
    description=
        "Join results from all the build slices"
)

subparsers.add_parser(
    "clear",
    aliases=[],
    help="Remove the dataset",
    description=
        "Removes the dataset folder so that the next build starts from scratch"
)

subparsers.add_parser(
    "build-preview",
    aliases=[],
    help="Builds a preview folder with an HTML file index"
)

subparsers.add_parser(
    "tar-dataset",
    aliases=[],
    help="Packages the resulting dataset in a tar file"
)


########
# Main #
########

args = parser.parse_args()

if args.command_name == "clear":
    assert os.system(f"rm -rf \"{SYNTHETIC_DATASET_PATH}\"") == 0
elif args.command_name == "build":
    build(
        slice_index=args.slice_index,
        slice_count=args.slice_count,
        inspect=args.inspect,
        linearize_only=args.linearize_only,
        soft=args.soft
    )
elif args.command_name == "finalize":
    finalize()
elif args.command_name == "build-preview":
    build_preview(
        dataset_path=SYNTHETIC_DATASET_PATH,
        slice_name="train"
    )
elif args.command_name == "tar-dataset":
    tar_path = os.path.realpath(SYNTHETIC_DATASET_PATH + ".tgz")
    assert os.system(
        f"cd {SYNTHETIC_DATASET_PATH} && tar -czvf {tar_path} " +
            f"samples/ " +
            f"samples.*.txt " +
            f"statistics.*.yaml " +
            f"vocabulary.txt"
    ) == 0
else:
    parser.print_help()
    exit(2)
