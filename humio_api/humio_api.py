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
        link = '%s/api/v1/dataspaces/humio/queryjobs' % self.baseUrl

        dt = {
            "queryString": queryString,
            "isLive": isLive,
            "timeZoneOffsetMinutes": timeZoneOffsetMinutes,
            "showQueryEventDistribution": showQueryEventDistribution,
            "start": start
        }

        r = requests.post(link, data=json.dumps(dt),
                          headers=self._getHeaders())

        print(r.status_code)
        print(r.json())
        self.getQueryResult(r.json()['id'])
        pass

    def getQueryResult(self, queryId):
        link = '%s/api/v1/dataspaces/humio/queryjobs/%s' % (
            self.baseUrl, queryId)

        r = requests.get(link,
                         headers=self._getHeaders())
        print(r.json())
        print(json.dumps(r.json(), indent=4, separators=(',', ': ')))
        pass

    def ingestJsonData(self, jsonDt=[]):
        link = '%s/api/v1/dataspaces/%s/ingest' % (
            self.baseUrl, self.dataspace)

        r = requests.post(link, data=json.dumps(jsonDt),
                          headers=self._getHeaders())

        print(r.text)
        pass

    # NOTE: user management
    def getUserList(self):
        link = '%s/api/v1/users' % self.baseUrl

        r = requests.get(link, headers=self._getHeaders())
        # self._preetyPrintJson(r.json())
        return r.json()

    def getUserByEmail(self, email):
        for user in self.getUserList():
            if email == user['email']:
                return user
        return None

    def createUser(self, email, isRoot=False):
        link = '%s/api/v1/users' % self.baseUrl

        dt = {
            'email': email,
            'isRoot': isRoot
        }

        r = requests.post(link, data=json.dumps(dt),
                          headers=self._getHeaders())
        # self._preetyPrintJson(r.json())
        pass

    def deleteUserById(self, userId):
        link = '%s/api/v1/users/%s' % (self.baseUrl, userId)

        r = requests.delete(link, headers=self._getHeaders())
        print(r.text)
        pass

    def deleteUserByEmail(self, email):
        pass

    # NOTE: helpers
    def preetyPrintJson(jsonDt):
        print(json.dumps(jsonDt, indent=4, separators=(',', ': ')))

    # NOTE: private methods
    def _getHeaders(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
