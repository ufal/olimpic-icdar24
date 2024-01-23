import argparse
from .generate import generate


##########
# Parser #
##########

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    title="available commands",
    dest="command_name"
)

subparsers.add_parser(
    "generate",
    aliases=[],
    help="Generates the test-dev-train dataset splits"
)


########
# Main #
########

args = parser.parse_args()

if args.command_name == "generate":
    generate()
else:
    parser.print_help()
    exit(2)
