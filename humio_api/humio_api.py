import requests
import json

versionNumberHumio = 'v1'

class HumioApi():

    def __init__(self, baseUrl='localhost:3000', dataspace='humio',
                 token='developer'):

        self.baseUrl = "http://{}".format(baseUrl)
        self.dataspace = dataspace
        self.token = token

    # experimental, for getting large files
    def initStreamingQuery(self, queryString='timechart()', isLive=False,
                           timeZoneOffsetMinutes=0, start='24hours', end='now'):

        link = '{}/api/{}/dataspaces/humio/query'.format(self.baseUrl, versionNumberHumio)

        dt = {
            'queryString': queryString,
            'isLive': isLive,
            'timeZoneOffsetMinutes': timeZoneOffsetMinutes,
            'start': start,
            'end': end
        }

        return requests.post(link, data=json.dumps(dt), headers=self._getHeaders(),
                             stream=True)

    def initQuery(self, queryString='timechart()', isLive=False,
                  timeZoneOffsetMinutes=0, showQueryEventDistribution=False,
                  start='24hours', end='now'):

        link = '{}/api/{}/dataspaces/humio/queryjobs'.format(self.baseUrl,versionNumberHumio)

        dt = {
            'queryString': queryString,
            'isLive': isLive,
            'timeZoneOffsetMinutes': timeZoneOffsetMinutes,
            'showQueryEventDistribution': showQueryEventDistribution,
            'start': start,
            'end': end
        }

        return requests.post(link, data=json.dumps(dt),
                             headers=self._getHeaders())

    def getQueryResult(self, queryId):
        link = '{}/api/{}/dataspaces/humio/queryjobs/{}'.format(
            self.baseUrl, versionNumberHumio, queryId)

        return requests.get(link, headers=self._getHeaders())

    def ingestJsonData(self, jsonDt=[]):
        link = '{}/api/{}/dataspaces/{}/ingest'.format(
            self.baseUrl, versionNumberHumio, self.dataspace)

        return requests.post(link, data=json.dumps(jsonDt),
                             headers=self._getHeaders())

    def ingestMessages(self, parser="json", messages=[]):
        link = '{}/api/{}/dataspaces/{}/ingest-messages'.format(
            self.baseUrl, versionNumberHumio, self.dataspace)
        obj = [{
            "type": parser,
            "messages": messages
        }]

        return requests.post(link, data=json.dumps(obj),
                             headers=self._getHeaders())

    # NOTE: user management
    def getUserList(self):
        link = '{}/api/{}/users'.format(self.baseUrl, versionNumberHumio)

        r = requests.get(link, headers=self._getHeaders())
        return r

    def getUserByEmail(self, email):
        userList = self.getUserList()
        for user in userList.json():
            if email == user['email']:
                return user
        return None

    def createUser(self, email, isRoot=False):
        link = '{}/api/{}/users'.format(self.baseUrl, versionNumberHumio)

        dt = {
            'email': email,
            'isRoot': isRoot
        }

        r = requests.post(link, data=json.dumps(dt),
                          headers=self._getHeaders())
        return r

    def deleteUserById(self, userId):
        link = '{}/api/{}/users/{}'.format(self.baseUrl, versionNumberHumio, userId)

        r = requests.delete(link, headers=self._getHeaders())
        return r.json()

    def deleteUserByEmail(self, email):
        for user in self.getUserList():
            if email == user['email']:
                return self.deleteUserById(user['userID'])
        return None

    # NOTE: helpers
    def prettyPrintJson(jsonDt):
        print(json.dumps(jsonDt, indent=4, separators=(',', ': ')))

    # NOTE: private methods
    def _getHeaders(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token),
#            'Accept-Encoding: gzip'
}