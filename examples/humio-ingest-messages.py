from humio_api.humio_api import HumioApi
import argparse
import json


def main(args):
    events = (open(args.sourceFile).readlines())

    api = HumioApi(baseUrl=args.host, repo=args.repo,
                   token=args.token)
    r = api.ingestMessages(parser="json", messages=events)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Handle humio api')

    parser.add_argument('--host', dest='host',
                        default='https://cloud.humio.com',
                        help='Humio host, default https://cloud.humio.com')

    parser.add_argument('--repo', dest='repo', required=True,
                        help='virtual or real repo name')

    parser.add_argument('--token', dest='token', required=True,
                        help='Humio API token')

    parser.add_argument('--file', dest='sourceFile', required=True,
                        help='Path to file with events (lines with json encoded events)')

    args = parser.parse_args()

    main(args)
