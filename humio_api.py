import requests
import json


class HumioApi:
    def __init__(self, baseUrl='http://localhost:3000', dataspace='humio', token='developer'):
        self.baseUrl = baseUrl
        self.dataspace = dataspace
        self.token = token

    def hadnleInitQuery(self, response):
        print(response.text)
        pass

    def initQuery(self, queryString="timechart()", isLive=False, timeZoneOffsetMinutes=0,
                  showQueryEventDistribution=False, start='24h'):
        queryjobsLink = '%s/api/v1/dataspaces/humio/queryjobs' % self.baseUrl

        dt = {
            "queryString": queryString,
            "isLive": isLive,
            "timeZoneOffsetMinutes": timeZoneOffsetMinutes,
            "showQueryEventDistribution": showQueryEventDistribution,
            "start": start
        }

        r = requests.post(queryjobsLink, data=json.dumps(dt),
                          headers=self._getHeaders())

        print(r.status_code)
        print(r.json())
        self.getQueryResult(r.json()['id'])
        pass

    def getQueryResult(self, queryId):
        pollQueryLink = '%s/api/v1/dataspaces/humio/queryjobs/%s' % (
            self.baseUrl, queryId)

        r = requests.get(pollQueryLink,
                         headers=self._getHeaders())
        print(r.json())
        print(json.dumps(r.json(), indent=4, separators=(',', ': ')))
        pass

    def ingestJsonData(self, jsonDt=[]):
        ingestLink = '%s/api/v1/dataspaces/%s/ingest' % (
            self.baseUrl, self.dataspace)

        print(ingestLink)
        r = requests.post(ingestLink, data=json.dumps(jsonDt),
                          headers=self._getHeaders())
        print(r.text)
        pass

    def _getHeaders(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
