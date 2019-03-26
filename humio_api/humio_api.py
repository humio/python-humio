import requests
import json

versionNumberHumio = 'v1'


class HumioApi():

    def __init__(self, baseUrl='http://localhost:3000', repo='humio',
                 token='developer'):

        self.baseUrl = "{}".format(baseUrl)
        self.repo = repo
        self.token = token

    # NOTE: experimental, for getting large files
    def initStreamingQuery(self, queryString='timechart()', isLive=False,
                           timeZoneOffsetMinutes=0, start='24hours', end='now'):

        link = '{}/api/{}/dataspaces/{}/query'.format(
            self.baseUrl, versionNumberHumio, self.repo)

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

        link = '{}/api/{}/dataspaces/{}/queryjobs'.format(
            self.baseUrl, versionNumberHumio, self.repo)

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
        link = '{}/api/{}/dataspaces/{}/queryjobs/{}'.format(
            self.baseUrl, versionNumberHumio, self.repo, queryId)

        return requests.get(link, headers=self._getHeaders())

    def ingestJsonData(self, jsonDt=[]):
        link = '{}/api/{}/dataspaces/{}/ingest'.format(
            self.baseUrl, versionNumberHumio, self.repo)

        return requests.post(link, data=json.dumps(jsonDt),
                             headers=self._getHeaders())

    def ingestMessages(self, parser="json", messages=[]):
        link = '{}/api/{}/dataspaces/{}/ingest-messages'.format(
            self.baseUrl, versionNumberHumio, self.repo)
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
        link = '{}/api/{}/users/{}'.format(self.baseUrl,
                                           versionNumberHumio, userId)

        r = requests.delete(link, headers=self._getHeaders())
        return r.json()

    def deleteUserByEmail(self, email):
        for user in self.getUserList():
            if email == user['email']:
                return self.deleteUserById(user['userID'])
        return None

    # NOTE: helpers
    def prettyPrintJson(jsonDt, out=None):
        if out:
            f = open(out, 'w')
            json.dump(jsonDt, f, indent=4, separators=(',', ': '))
            f.close()
        else:
            print(json.dumps(jsonDt, indent=4, separators=(',', ': ')))

    # NOTE: private methods
    def _getHeaders(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token),
        }

    # NOTE: files API

    def uploadFile(self, filePath):
        link = '{}/api/{}/dataspaces/{}/files'.format(
            self.baseUrl, versionNumberHumio, self.repo)
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
        }
        return requests.post(link, files={'file': open(filePath, 'rb')},
                             headers=headers)

    def listFiles(self):
        link = '{}/graphql'.format(self.baseUrl)
        headers = self._getHeaders()
        request = {
            'query': 'query {{listUploadedFiles(name:\"{}\")}}'.format(self.repo),
            'variables': None
        }
        result = requests.post(link, headers=headers, data = json.dumps(request))
        return result.json()['data']['listUploadedFiles']

    def getFile(self, fileName):
        link = '{}/api/{}/dataspaces/{}/files/{}'.format(
            self.baseUrl, versionNumberHumio, self.repo, fileName)
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
        }
        return requests.get(link, headers=headers)
