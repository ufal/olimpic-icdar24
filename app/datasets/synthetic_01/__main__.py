import argparse
from .prepare import prepare


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

subparsers.add_parser(
    "prepare",
    aliases=[],
    help="Prepare the dataset",
    description=
        "Builds the dataset up from the downloaded Open Score " + \
        "Lieder corpus."
)


########
# Main #
########

args = parser.parse_args()

if args.command_name == "prepare":
    prepare()
else:
    parser.print_help()
    exit(2)
