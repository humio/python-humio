from humio_api.humio_api import HumioApi
import argparse
import time


def printProgressBar(workDone):
    barLen = 50
    workDoneBar = round(workDone * float(barLen)/100)

    bar = '[' + ''.join('█' for _ in range(workDoneBar)) + \
        ''.join('.' for _ in range(barLen - workDoneBar)) + ']'

    print('{} {}% done'.format(bar, workDone), end='\r')


def main(args):
    api = HumioApi(baseUrl=args.host, repo=args.repo,
                   token=args.token)

    print('Running query')
    printProgressBar(0)

    # creating query

    start = int(args.start) if args.start.isdigit() else args.start
    end = int(args.end) if args.end.isdigit() else args.end

    initQueryRes = api.initQuery(
        queryString=args.query, start=start, end=end)

    # getting query result
    if initQueryRes.status_code == 200:
        queryId = initQueryRes.json()['id']
        done = False
        while not done:
            res = api.getQueryResult(queryId)
            if res.status_code == 200:
                jsonRes = res.json()
                done = jsonRes['done']
                if not done:
                    workDone = float(
                        jsonRes['metaData']['workDone'])/jsonRes['metaData']['totalWork']

                    printProgressBar(round(workDone*100.0))

                    time.sleep(float(jsonRes['metaData']['pollAfter'])/1000)
            else:
                break
        printProgressBar(100)
        print()
        HumioApi.prettyPrintJson(res.json(), args.out)
    elif (initQueryRes.status_code >= 400):
        print()
        print('Error! Wrong query.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Humio query')

    parser.add_argument('--host', dest='host',
                        default='https://cloud.humio.com',
                        help='Humio host, default https://cloud.humio.com')

    parser.add_argument('--repo', dest='repo', required=True,
                        help='virtual or real repo name')

    parser.add_argument('--token', dest='token', required=True,
                        help='Humio API token')

    parser.add_argument('--query', dest='query',
                        help='Humio query string')

    parser.add_argument('--start', dest='start', default='24hours',
                        help='Humio query start time')

    parser.add_argument('--end', dest='end', default='now',
                        help='Humio query end time')

    parser.add_argument('--out', dest='out', default=None,
                        help='Result out file.')

    args = parser.parse_args()

    main(args)
