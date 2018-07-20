from humio_api.humio_api import HumioApi
import argparse
import time

def uploadFile(api, filePath):
    print(api.uploadFile(filePath).text)

def listFiles(api):
    print(api.listFiles())

def getFileContent(api, fileName):
    print(api.getFile(fileName).text)

def main(args):
    api = HumioApi(baseUrl=args.host, repo=args.repo,
                   token=args.token)

    if args.uploadFile:
        uploadFile(api, args.uploadFile)

    if args.listFiles:
        listFiles(api)

    if args.getFile:
        getFileContent(api, args.getFile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Handle humio api')

    parser.add_argument('--host', dest='host',
                        default='https://cloud.humio.com',
                        help='Humio host, default https://cloud.humio.com')

    parser.add_argument('--repo', dest='repo', required=True,
                        help='virtual or real repo name')

    parser.add_argument('--token', dest='token', required=True,
                        help='Humio API token')

    parser.add_argument('--uploadFile', dest='uploadFile', default=None,
                        help='Path to file to upload')

    parser.add_argument('--listFiles', dest='listFiles', default=None,
                        help='List uploaded files', action="store_true")

    parser.add_argument('--getFile', dest='getFile', default=None,
                        help='Get uploaded file content')

    args = parser.parse_args()

    main(args)
