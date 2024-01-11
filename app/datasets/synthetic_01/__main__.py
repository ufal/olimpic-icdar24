import argparse
from .clear import clear
from .build import build
from .finalize import finalize


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
    "--msq_only", action="store_true", default=False,
    help="Only process the semantic data, not images (MXL, MSQ)"
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


########
# Main #
########

args = parser.parse_args()

if args.command_name == "clear":
    clear()
elif args.command_name == "build":
    build(
        slice_index=args.slice_index,
        slice_count=args.slice_count,
        inspect=args.inspect,
        msq_only=args.msq_only
    )
elif args.command_name == "finalize":
    finalize()
else:
    parser.print_help()
    exit(2)
