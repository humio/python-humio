"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mhumiolib` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``humiolib.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``humiolib.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import json
from humiolib.HumioClient import HumioClient, HumioIngestClient
from humiolib.HumioExceptions import HumioException

def command_ingest(client, args):
    api = client

    fields = dict(args.field) if args.field else None
    tags = dict(args.tag) if args.tag else None

    if fields:
        print("[*] Adding fields: ")
        print(json.dumps(fields, indent=2))

    if tags:
        print("[*] Adding tags: ")
        print(json.dumps(tags, indent=2))

    if args.parser:
        print("[*] Applying parser '" + args.parser + "'")

    if args.file:
        print("[*] Uploading events from '" + args.file + "'")
        with open(args.file) as sourceFile:
            events = list(
                line.strip() for line in sourceFile.readlines() if line.strip()
            )
            try:
                api.ingest_messages(
                    messages=events, parser=args.parser, fields=fields, tags=tags
                )
                print("[OK]")
            except HumioException as e:
                print(e)

    if args.interactive:
        print("[*] Starting interactive mode")
        inp = input(">>")
        while inp:
            try:
                api.ingest_messages(
                    messages=[inp], parser=args.parser, fields=fields, tags=tags
                )
                print("[OK]")
            except HumioException as e:
                print(e)
            inp = input(">>")


parser = argparse.ArgumentParser(description="Command description.")
parser.add_argument(
    "--host",
    dest="host",
    default="https://cloud.humio.com",
    help="Humio host (default: https://cloud.humio.com)",
)
parser.add_argument(
    "-r", "--repository", default=None, help="virtual or real repository name"
)

token_group = parser.add_mutually_exclusive_group()
token_group.add_argument("-u", "--user-token", default=None, help="Humio user token")
token_group.add_argument("-t", "--ingest-token", default=None, help="Humio ingest token")

commands = parser.add_subparsers(help="Possible commands")
ingest_parser = commands.add_parser("ingest", help="Ingest data to Humio")
ingest_parser.set_defaults(func=command_ingest)


ingest_parser.add_argument(
    "-p",
    "--parser",
    default=None,
    help="The parser to use (this does not work if there is a parser attached to the ingest token)",
)
ingest_parser.add_argument(
    "--field",
    default=[],
    action="append",
    nargs=2,
    metavar=("FIELD", "VALUE"),
    help="Add a field to all events (example: `--field source cli`)",
)
ingest_parser.add_argument(
    "--tag",
    default=[],
    action="append",
    nargs=2,
    metavar=("TAG", "VALUE"),
    help="Add a tag to all events (example: `--tag source cli`) NOTE: This may have performance impacts on Humio",
)

ingest_parser.add_argument(
    "-f", "--file", default=None, help="Path to file with raw events on each line"
)
ingest_parser.add_argument(
    "-i",
    "--interactive",
    default=False,
    action="store_true",
    help="Start REPL to send one event per line",
)


def main(args=None):
    args = parser.parse_args(args=args)

    if args.ingest_token:
        client = HumioIngestClient(
            base_url=args.host,
            ingest_token=args.ingest_token
        )
    else:
        client = HumioClient(
            base_url=args.host,
            repository=args.repository,
            user_token=args.user_token
        )

    args.func(client, args)
