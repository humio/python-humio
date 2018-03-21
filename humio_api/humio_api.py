import requests
import json


class HumioApi:
    def __init__(self, baseUrl='http://localhost:3000', dataspace='humio',
                 token='developer'):

        self.baseUrl = baseUrl
        self.dataspace = dataspace
        self.token = token

    # experimental, for getting lage files
    def initStreamingQuery(self, queryString='timechart()', isLive=False,
                           timeZoneOffsetMinutes=0, start='24h'):

        link = '%s/api/v1/dataspaces/humio/query' % self.baseUrl

        dt = {
            'queryString': queryString,
            'isLive': isLive,
            'timeZoneOffsetMinutes': timeZoneOffsetMinutes,
            'start': start
        }

        return requests.post(link, data=json.dumps(dt), headers=self._getHeaders(),
                             stream=True)

    def initQuery(self, queryString='timechart()', isLive=False,
                  timeZoneOffsetMinutes=0, showQueryEventDistribution=False,
                  start='24h'):

        link = '%s/api/v1/dataspaces/humio/queryjobs' % self.baseUrl

        dt = {
            'queryString': queryString,
            'isLive': isLive,
            'timeZoneOffsetMinutes': timeZoneOffsetMinutes,
            'showQueryEventDistribution': showQueryEventDistribution,
            'start': start
        }

        return requests.post(link, data=json.dumps(dt),
                             headers=self._getHeaders())

    def getQueryResult(self, queryId):
        link = '%s/api/v1/dataspaces/humio/queryjobs/%s' % (
            self.baseUrl, queryId)

        return requests.get(link, headers=self._getHeaders())

    def ingestJsonData(self, jsonDt=[]):
        link = '%s/api/v1/dataspaces/%s/ingest' % (
            self.baseUrl, self.dataspace)

        return requests.post(link, data=json.dumps(jsonDt),
                             headers=self._getHeaders())

    def ingestMessages(self, parser="json", messages=[]):
        link = '%s/api/v1/dataspaces/%s/ingest-messages' % (
            self.baseUrl, self.dataspace)
        obj = [{
            "type": parser,
            "messages": messages
        }]

        return requests.post(link, data=json.dumps(obj),
                             headers=self._getHeaders())

    # NOTE: user management
    def getUserList(self):
        link = '%s/api/v1/users' % self.baseUrl

        r = requests.get(link, headers=self._getHeaders())
        return r

    def getUserByEmail(self, email):
        userList = self.getUserList()
        for user in userList.json():
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
        return r

    def deleteUserById(self, userId):
        link = '%s/api/v1/users/%s' % (self.baseUrl, userId)

        r = requests.delete(link, headers=self._getHeaders())
        return r.json()

    def deleteUserByEmail(self, email):
        for user in self.getUserList():
            if email == user['email']:
                return self.deleteUserById(user['userID'])
        return None

    # NOTE: helpers
    def preetyPrintJson(jsonDt):
        print(json.dumps(jsonDt, indent=4, separators=(',', ': ')))

    # NOTE: private methods
    def _getHeaders(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
