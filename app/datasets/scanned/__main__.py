import argparse
from ..config import SCANNED_DATASET_PATH
from .load_workbench import load_workbench
from .save_workbench import save_workbench
from .prepare_imslp_pngs import prepare_imslp_pngs
from .build import build
from ..build_preview import build_preview
from .finalize import finalize
from .progress import progress


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

subparsers.add_parser(
    "prepare-imslp-pngs",
    aliases=[],
    help="Converts IMSLP PDFs to images and checks their presence"
)

build_parser = subparsers.add_parser(
    "build",
    aliases=[],
    help="Builds samples from the manually created annotation files"
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

subparsers.add_parser(
    "save-workbench",
    aliases=[],
    help="Creates the workbench inkscape file for a given corpus score ID"
)

subparsers.add_parser(
    "build-preview",
    aliases=[],
    help="Builds a preview folder with an HTML file index"
)

subparsers.add_parser(
    "progress",
    aliases=[],
    help="Prints the annotation progress for the scanned test and dev partitions"
)


########
# Main #
########

args = parser.parse_args()

# annotation commans
if args.command_name == "prepare-imslp-pngs":
    prepare_imslp_pngs()
elif args.command_name == "load-workbench":
    load_workbench(args.score_id)
elif args.command_name == "save-workbench":
    save_workbench()
elif args.command_name == "progress":
    progress()

# final export commands
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
        dataset_path=SCANNED_DATASET_PATH,
        slice_name="test"
    )

else:
    parser.print_help()
    exit(2)
